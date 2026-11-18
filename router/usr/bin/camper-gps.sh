#!/bin/sh
# ============================================================
# SMART CAMPER - router GPS -> Home Assistant sender   (v1)
# On the router (GL-X3000):  /usr/bin/camper-gps.sh
# Started at boot by /etc/init.d/camper-gps (procd restarts it if it stops).
# Needs nothing extra: BusyBox sh/awk + curl, both already on the router.
#
# CHANGELOG
#   v1 - 2026-10-21. Replaces the GPS sender lost in the 2026-10-20 factory
#        reset. HA side: package camper_gps.yaml v1 (webhook glnet_router_gps).
#
#        SOURCE: the modem's GPS stream /dev/mhi_LOOPBACK (NMEA, 1 per second).
#          $GPRMC -> fix A/V, latitude, longitude, speed (knots), heading
#          $GPGGA -> satellites used, HDOP (precision), altitude (m)
#        The stream is read CONTINUOUSLY. Lines nobody reads pile up in it:
#        measured 2026-10-20, a line read at 20:10:21 UTC was stamped 20:07:11
#        (190 s old). So at start the backlog is thrown away first (5 s), and
#        from then on every line is read as it arrives.
#
#        SENDS only when RMC status = A (real fix), to
#        http://homeassistant.local:8123/api/webhook/glnet_router_gps
#          - every 10 s while speed > 5 km/h
#          - every 300 s when parked
#          - at once when it switches between moving and parked
#        Speed: knots x 1.852 = km/h.
#        JSON: {"lat","lon","speed" km/h,"heading" deg|null,"alt" m,"sats",
#               "hdop","fix","time" GPS UTC}
#        Bad lines are dropped by the NMEA checksum.
#
#        LOG:  logread -e camper-gps   (start, fix lost/back, send errors)
#        TEST without sending anything:  DRY=1 /usr/bin/camper-gps.sh
#             prints the JSON it would send; Ctrl+C to stop.
# ============================================================

DEV="${DEV:-/dev/mhi_LOOPBACK}"
URL="${URL:-http://homeassistant.local:8123/api/webhook/glnet_router_gps}"
MOVING_KMH=5        # above this = moving
MOVING_EVERY=10     # seconds between sends while moving
PARKED_EVERY=300    # seconds between sends while parked
DRAIN_S="${DRAIN_S:-5}"   # seconds of old backlog to throw away at start
DRY="${DRY:-0}"

say() {
    logger -t camper-gps "$*"
    [ "$DRY" = 1 ] && echo "# $*"
}

# The stream appears a little after the modem starts at boot.
while [ ! -e "$DEV" ]; do sleep 5; done

# Throw away the backlog so the first position sent is the current one.
[ "$DRAIN_S" -gt 0 ] && timeout "$DRAIN_S" cat "$DEV" > /dev/null 2>&1

say "started, sending to $URL"

# exec: awk becomes this process, so procd stops/restarts it directly.
exec awk -v url="$URL" -v mv="$MOVING_KMH" -v fast="$MOVING_EVERY" \
    -v slow="$PARKED_EVERY" -v dry="$DRY" '

function say(m) {
    system("logger -t camper-gps " q m q)
    if (dry == 1) { print "# " m; fflush() }
}

# NMEA checksum = XOR of every character between "$" and "*".
function nmea_ok(s,    p, body, cs, i) {
    if (substr(s, 1, 1) != "$") return 0
    p = index(s, "*")
    if (p < 3 || length(s) < p + 2) return 0
    body = substr(s, 2, p - 2)
    cs = 0
    for (i = 1; i <= length(body); i++) cs = xor(cs, ord[substr(body, i, 1)])
    return sprintf("%02X", cs) == toupper(substr(s, p + 1, 2))
}

# ddmm.mmmm / dddmm.mmmm -> decimal degrees (S and W negative)
function deg(v, h,    d) {
    d = int(v / 100)
    v = d + (v - d * 100) / 60
    return (h == "S" || h == "W") ? -v : v
}

function num(v) { return (v == "") ? "null" : sprintf("%g", v + 0) }

function send(j,    cmd, code) {
    if (dry == 1) { print j; fflush(); return }
    cmd = "curl -s -m 5 -o /dev/null -w " q "%{http_code}" q \
          " -X POST -H " q "Content-Type: application/json" q \
          " -d " q j q " " q url q
    code = ""
    cmd | getline code
    close(cmd)
    if (code == "200") {
        if (failing) say("sending to HA works again")
        else if (!sent) say("first position sent to HA")
        failing = 0; sent = 1
    } else if (!failing) {
        failing = 1
        say("sending to HA failed (HTTP " code "), will keep trying")
    }
}

BEGIN {
    q = sprintf("%c", 39)
    for (i = 32; i < 127; i++) ord[sprintf("%c", i)] = i
    last = -1; lastmv = -1; fix = -1
    sats = ""; hdop = ""; alt = ""
}

{
    sub(/\r$/, "")
    if (!nmea_ok($0)) next
    n = split(substr($0, 1, index($0, "*") - 1), f, ",")
    t = substr(f[1], 4)

    if (t == "GGA" && n >= 10) {
        sats = f[8]; hdop = f[9]; alt = f[10]
        next
    }
    if (t != "RMC" || n < 10) next

    if (f[3] != "A" || f[4] == "" || f[6] == "") {
        if (fix != 0) say("no GPS fix - not sending")
        fix = 0
        next
    }
    if (fix != 1) say("GPS fix OK")
    fix = 1

    kmh = (f[8] + 0) * 1.852
    moving = (kmh > mv) ? 1 : 0
    now = substr(f[2], 1, 2) * 3600 + substr(f[2], 3, 2) * 60 + substr(f[2], 5, 2)
    gap = (last < 0) ? 999999 : (now - last + 86400) % 86400

    if (moving != lastmv || gap >= (moving ? fast : slow)) {
        send(sprintf("{\"lat\":%.6f,\"lon\":%.6f,\"speed\":%.1f,\"heading\":%s,\"alt\":%s,\"sats\":%s,\"hdop\":%s,\"fix\":\"A\",\"time\":\"20%s-%s-%sT%s:%s:%sZ\"}",
            deg(f[4] + 0, f[5]), deg(f[6] + 0, f[7]), kmh,
            (f[9] == "" ? "null" : sprintf("%.1f", f[9] + 0)),
            num(alt), num(sats), num(hdop),
            substr(f[10], 5, 2), substr(f[10], 3, 2), substr(f[10], 1, 2),
            substr(f[2], 1, 2), substr(f[2], 3, 2), substr(f[2], 5, 2)))
        last = now; lastmv = moving
    }
}

END { say("GPS stream ended - procd restarts this in 10 s") }
' "$DEV"
