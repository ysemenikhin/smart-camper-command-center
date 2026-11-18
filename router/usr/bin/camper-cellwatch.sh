#!/bin/sh
# ============================================================
# SMART CAMPER - modem 3G "stuck" watchdog   (v1)
# On the router (GL-X3000):  /usr/bin/camper-cellwatch.sh
# Started at boot by /etc/init.d/camper-cellwatch (procd restarts it).
# Needs nothing extra: BusyBox sh + gl_modem, both already on the router.
#
# CHANGELOG
#   v1 - 2026-10-28. WHY: with network mode AUTO the modem dropped to 3G
#        (WCDMA) while parked and STAYED there - cellular is idle (NOCONN)
#        because the Wi-Fi repeater is the WAN, so nothing pushes it back.
#        Proven 2026-10-28 at the same parking spot: AUTO -> WCDMA
#        (RSCP -78, Ec/Io -5); forcing LTE:NR5G -> LTE band 3 at once
#        (RSRP -91, RSRQ -12, SINR 13). LTE was there all along.
#
#        WHAT IT DOES - network mode stays AUTO; only if the modem sits on
#        3G/2G for STUCK_MIN minutes in a row:
#          1. lock LTE:NR5G         AT+QNWPREFCFG="mode_pref",LTE:NR5G
#          2. wait up to TEST_S s for it to register on LTE / NR5G-SA
#          3. set AUTO back in EVERY case. If LTE was found the modem stays
#             on it under AUTO (seen 2026-10-28); if not, nothing lost.
#          4. after a failed test, wait STUCK_MIN again before the next.
#        Never touches a mode that is NOT AUTO (a manual lock is respected).
#        If the script is stopped mid-test it puts AUTO back first.
#
#        Modem bus 1-1.2 (from /proc/gl-hw-info/build-in-modem; both IDs in
#        that file answer, 1-1.2 is the one used in testing).
#
#        LOG:  logread -e camper-cellwatch
#        TEST without changing anything:  DRY=1 /usr/bin/camper-cellwatch.sh
#             logs and prints what it WOULD do; Ctrl+C to stop.
# ============================================================

BUS="${BUS:-1-1.2}"
CHECK_EVERY="${CHECK_EVERY:-60}"   # seconds between checks
STUCK_MIN="${STUCK_MIN:-30}"       # minutes on 3G/2G before a test
TEST_S="${TEST_S:-120}"            # seconds to wait for LTE during a test
DRY="${DRY:-0}"
TESTING=0

say() {
    logger -t camper-cellwatch "$*"
    [ "$DRY" = 1 ] && echo "# $*"
}

at() { gl_modem -B "$BUS" AT "$1" 2>/dev/null; }

# Network type from the serving cell: LTE, NR5G-SA, WCDMA, GSM ...
# Empty when searching / no service.
mode_now() {
    at 'AT+QENG="servingcell"' | awk -F, '/\+QENG: "servingcell"/ {
        gsub(/"/, "", $3); print $3; exit }'
}

pref_now() {
    at 'AT+QNWPREFCFG="mode_pref"' | awk -F, '/\+QNWPREFCFG:/ {
        gsub(/[" \r]/, "", $2); print $2; exit }'
}

set_pref() {
    if [ "$DRY" = 1 ]; then say "DRY: would set mode_pref $1"; return 0; fi
    at "AT+QNWPREFCFG=\"mode_pref\",$1" | grep -q 'OK'
}

restore_auto() {
    if [ "$TESTING" = 1 ]; then
        set_pref AUTO && say "stopped mid-test - mode put back to AUTO"
        TESTING=0
    fi
}
trap 'restore_auto; exit 0' INT TERM

say "started (bus $BUS, test after ${STUCK_MIN} min on 3G)"
stuck=0
need=$(( STUCK_MIN * 60 / CHECK_EVERY ))

while true; do
    m=$(mode_now)
    case "$m" in
        WCDMA|GSM|HSPA*|TDSCDMA)
            stuck=$(( stuck + 1 ))
            [ "$stuck" = 1 ] && say "modem on $m - watching"
            ;;
        *)
            [ "$stuck" -gt 0 ] && say "modem back on ${m:-no service}"
            stuck=0
            ;;
    esac

    if [ "$stuck" -gt 0 ] && [ "$stuck" -ge "$need" ]; then
        p=$(pref_now)
        if [ "$p" != "AUTO" ]; then
            say "on $m for ${STUCK_MIN} min but mode is '$p' (not AUTO) - leaving it alone"
        else
            say "on $m for ${STUCK_MIN} min - testing LTE:NR5G"
            TESTING=1
            if set_pref LTE:NR5G; then
                found=""
                t=0
                while [ "$t" -lt "$TEST_S" ]; do
                    sleep 10; t=$(( t + 10 ))
                    m2=$(mode_now)
                    case "$m2" in LTE|NR5G*) found="$m2"; break ;; esac
                done
                set_pref AUTO
                TESTING=0
                if [ -n "$found" ]; then
                    say "LTE test OK - modem on $found after ${t}s, mode back to AUTO"
                else
                    say "LTE test: no LTE/5G within ${TEST_S}s - mode back to AUTO, next try in ${STUCK_MIN} min"
                fi
            else
                TESTING=0
                say "could not set LTE:NR5G - modem did not answer OK"
            fi
        fi
        stuck=0
    fi
    sleep "$CHECK_EVERY"
done
