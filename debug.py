import pandas as pd
from pyparsing import *
from utils import *

texttest = """
Record Number 1802
Weapon Scoring
            Application ID: 13
               Record Type: 3
            Record Subtype: 2
               Minor Frame: 01196646
                Time (UTC): 18:41:47.563
          Recording Length: 284 (16-bit words)
               Tail Number: 0
                 Tail Year: 0
                      Date: 07/28/20
                      Mode: STRIKE
Launch

PERTINENT DATA
    Dev ID                                        LP3                               (0x0000003C)
    WPN Mode Switches                                                               (0x0000003E)
        In Go NoGo Test                           False                      
        In SIT                                    False                      
        ECU Override Sel                          False                      
        Manual LNCH Enabled                       True                      
        Auto TGTING Enabled                       False                      
        GPS Keys Avail In ACU                     True                      
        LCD In Progress                           False                      
        JETT In Progress                          False                      
        Left WIU Unlock Enabled                   True                      
        Right WIU Unlock Enabled                  False                      
        Two Man Unlock Consent Enabled            True                      
        Any MDT In Progress                       False                      
        TDS Mod Act                               False                      
        War MSN                                   True                      
        Ferry MSN                                 False                      
        Operational Test LNCH                     False                      
        TLI MSN                                   False                      
        JTU                                       False                      
        Captive Carry MSN                         False                      
    Latitude                                      N 040:29.4333  deg                (0x00000042)
    Longitude                                     W 113:21.9649  deg                (0x00000046)
    Altitude                                      + 26014.00000  feet               (0x0000004A)
    True Heading                                  + 070.2440033  deg                (0x0000004E)
    GND Trk Angle                                 + 071.9620285  deg                (0x00000052)
    Pitch Angle                                   - 000.6811523  deg                (0x00000056)
    Roll Angle                                    + 000.3719696  deg                (0x0000005A)
    Yaw Angle                                     - 070.0598145  deg                (0x0000005E)
    Velocity North                                  224.0614471  ft/sec             (0x00000062)
    Velocity East                                   688.0382690  ft/sec             (0x00000066)
    Velocity Vertical                               003.5946419  ft/sec             (0x0000006A)
    GND Speed                                       723.6022339  ft/sec             (0x0000006E)
    True Air Speed North                          + 0225.466919  ft/sec             (0x00000072)
    True Air Speed East                           + 628.2985840  ft/sec             (0x00000076)
    Prime Nav Info                                                                  (0x0000007A)
        Prime INU Mode                            INU1                      
        Prime Nav System                          INU1                      
    WPN TGT Status Word                                                             (0x0000007E)
        TDS 1 Valid                               True                      
        TDS 2 Valid                               True                      
        Primary TGT Location                      2                      
        Tgt Store Loc Num                         2                      
    WPN Status 22T02                                                                (0x00000080)
        Safe To Release                           True                      
        Crit HW Passed                            True                      
        Min TXA RCVD                              True                      
        Min TDS RCVD                              True                      
        AUR Ready                                 True                      
        TXA Good                                  True                      
        MIN GPS Data                              True                      
        Last BIT Passed                           True                      
        Warm Up Complete                          True                      
        Release Consent                           False                      
        Commit To Sep Store                       True                      
        TM Present                                False                      
        PF Present                                False                      
        AJ AEM Present                            False                      
        PWR Interruption                          False                      
        Timeline Aborted                          False                      
    WPN Status 22T03                                                                (0x00000082)
        Modify TGT Data RCVD                      True                      
        Almanac RCVD                              True                      
        Ephemeris RCVD                            True                      
        AS SV RCVD                                True                      
        GPS Keys RCVD                             True                      
        Time RCVD                                 True                      
        CNM RCVD                                  False                      
        GPS Key Failed CHKSum                     False                      
        PF Program Status                         True                      
        GPS Keys Loading                          False                      
    WPN State                                                                       (0x00000084)
        WPN PWR State                             Off                      
        WPN Type                                  J1                      
        IBIT In Progress                          False                      
        WPN Present                               False                      
        TGTed                                     False                      
        TGTING In Progress                        False                      
        Direct TGT                                True                      
        MSN Planned TGT                           False                      
        Captive Carry Launched                    False                      
        CTS Battery Activated                     True                      
        Manual LNCH Required                      False                      
        Wpn LNCH In Progress                      False                      
        IR Status                                 Inside                      
        IZ Status                                 Inside                      
        AC Store Station ID RCVD                  True                      
        GPS Config                                Non SAASM                      
    WPN Alignment State                                                             (0x0000008A)
        GPS Nav Halted                            False                      
        TXA Halted                                False                      
        TXA Quality                               1                      
        Satellites Tracked                        0                      
        NAV Solution Quality                      Good                      
    WPN Status 22T24                                                                (0x0000008C)
        Fuze Type                                 0                      
        Fuze Variant                              0                      
    WPN Bit 22T09                                                                   (0x0000008E)
        Processor Good                            True                      
        GPS Good                                  True                      
        CS Good                                   True                      
        IMU Good                                  True                      
        PS Good                                   True                      
        TIK Good                                  True                      
        Squibs Good                               True                      
        PF Good                                   True                      
        Aj AEM Good                               True                      
        Laser Kit Good                            True                      
    WPN Test 22T10                                                                  (0x00000090)
        TXA Reinitiated                           False                      
        TM On                                     False                      
        TXA Halted                                False                      
        GPS Nav Halted                            False                      
        In SIM Flight                             False                      
        GPS Acq Started                           False                      
        In Timeline Intg                          False                      
        Sim Rlse Countdown                        False                      
    Last AIU 1553 Status Word                                                       (0x00000092)
        Remote Term Address                       11                      
        Message Error                             False                      
        Instrumentation                           True                      
        Service Req                               False                      
        Broadcast RCVD                            False                      
        Busy                                      False                      
        Subsys Failure                            False                      
        Dynamic Control                           False                      
        Remote Term Failure                       False                      
    WCD System Status                                                               (0x00000094)
        IDC PWR Enable Status                     False                      
        Bay Store DC PWR Status                   False                      
        RP Store DC PWR Status                    True                      
        LP Store DC PWR Status                    True                      
        ECU PWR Status                            True                      
        Environmental No Go Monitor               False                      
        Bay Door Close Monitor                    False                      
        Bay Door Open Monitor                     True                      
    WCD Expected Status                                                             (0x00000096)
        IDC PWR Enable Status                     False                      
        Bay Store DC PWR Status                   False                      
        RP Store DC PWR Status                    True                      
        LP Store DC PWR Status                    True                      
        ECU PWR Status                            True                      
        Environmental No Go Monitor               False                      
    WIU BIT Error Map                                                               (0x00000098)
        Initial PWR                               False                      
        Unauthorized Write                        False                      
        Window Open Time Expired                  False                      
        Extra Write                               False                      
        Out Of Tolerance 5V                       False                      
        Window Open                               False                      
        RTC Response Error                        False                      
        Handshake Resp Error                      False                      
        BIT Error Code                            0                      
    WIU PWR Discrete Status                                                         (0x0000009A)
        Ejector Locked                            False                      
        Ejector Unlocked                          True                      
        Ejector WPN Present                       False                      
        Ejector Arm Solenoid                      On                      
        Umbilical WPN Present                     False                      
        PWR 28 VDC 1                              Off                      
        PWR 28 VDC 2                              Off                      
        PWR 115 VAC                               Off                      
        Comm 1553B Failed                         False                      
        Instrumentation Present                   False                      
        Service Req                               False                      
        Broadcast CMD RCVD                        False                      
        RT Subsys Busy                            False                      
        Subsys FLT Flag                           False                      
        RT Term Failed                            False                      
    WIU Ejector Status                                                              (0x0000009C)
        Ejector Unlock CMDed                      False                      
        Ejector Squib Fire CMDed                  False                      
        Release Consent CMDed                     False                      
        Left Unlock Enabled                       True                      
        Right Unlock Enabled                      True                      
        Ejectors 8                                False                      
        Ejectors 7                                False                      
        Ejectors 6                                False                      
        Ejectors 5                                False                      
        Ejectors 4                                False                      
        Ejectors 3                                False                      
        Ejectors 2                                False                      
        Ejectors 1                                False                      
    MSN Data ACCUM MSN Time                         003:17:57.3846  hr,min,sec      (0x000000A0)
    Speed of Sound Ft Per Sec                       1045.1602  ft/sec               (0x000000A4)
    ATMOS Density Slugs Per CuFt                    000.0010  slug/ft3              (0x000000A8)
    Alternate Nav Mode                                                              (0x000000AC)
        Velocity                                  Doppler                      
        Attitude                                  AHRS                      
        Heading                                   AHRS                      
        Manual Mode                               True                      
    WPN Group ID                                                                    (0x000000B4)
    TGTING Data                                                                     (0x000000B6)
        TGTING Mode                               Direct TGT                      
        MSN Group                                 0                      
        LP DT Num                                 127                      
    TGT Header                                    0                                 (0x000000BE)
    TGT Invalidity                                                                  (0x000000C0)
        ID Invalid                                False                      
        Type Invalid                              False                      
        Name Invalid                              False                      
        Position Invalid                          False                      
        Impact Azimuth Invalid                    True                      
        Impact Angle Invalid                      False                      
        Offsets Invalid                           False                      
        Relative TGTING Invalid                   False                      
        Min Impact Vel Invalid                    False                      
        TGT Vel Invalid                           True                      
        Laser Code Invalid                        True                      
        Laser CCM Invalid                         False                      
    TGT Target ID                                 65535                             (0x000000C2)
    TGT Type                                                                        (0x000000C4)
        TGT Alt Ref                               MSL                      
        PF Control Source                         PF If Present                      
        TGT Orientation                           Horizontal                      
        Attack Mode                               Bomb On Coordinates                      
        TGT Hardness                              Not Specified                      
    TGT Name                                                                        (0x000000C6)
    TGT LAT                                       N 040:30.2001  deg                (0x000000D6)
    TGT LONG                                      W 113:17.7164  deg                (0x000000DA)
    TGT Altitude                                  + 01405.43  meters                (0x000000DE)
    Min Impact Velocity                                                             (0x000000E2)
        Minimum Impact Velocity                   0  meters/sec          
    Impact Azimuth                                0  deg                            (0x000000E4)
    Impact Angle                                  90  deg                           (0x000000E6)
    TGT Vel North                                 + 000.0000  meters/sec            (0x000000E8)
    TGT Vel East                                  + 000.0000  meters/sec            (0x000000EA)
    Laser Code                                                                      (0x000000EC)
        Laser Code 1                              0                      
        Laser Code 2                              0                      
        Laser Code 3                              0                      
        Laser Code 4                              0                      
    Laser CCM                                                                       (0x000000EE)
        Last Pulse Logic                          Long Last Pulse Logic                      
        Inhibit Laser                             True                      
        Stationary TGT                            True                      
        Basis for TGT Position                    False                      
    Offset North                                  + 00000.0  meters                 (0x000000F0)
    Offset East                                   + 00000.0  meters                 (0x000000F2)
    Offset Down                                   + 00000.0  meters                 (0x000000F4)
    Relative TGT SV1                                                                (0x000000F6)
        Channel 1 ID                              0                      
        Channel 2 ID                              0                      
        Channel 3 ID                              0                      
    Relative TGT SV2                                                                (0x000000F8)
        Channel 4 ID                              0                      
    PF Record/Block Num                                                             (0x000000FA)
        Record Num                                1                      
        Block Number                              2                      
    PF Invalidity Word 1                                                            (0x000000FC)
        Word 1 Invalid                            False                      
        Word 2 Invalid                            False                      
        Word 3 Invalid                            False                      
        Word 4 Invalid                            False                      
        Word 5 Invalid                            False                      
        Word 6 Invalid                            False                      
        Word 7 Invalid                            False                      
        Word 8 Invalid                            True                      
        Word 9 Invalid                            True                      
        Word 10 Invalid                           False                      
        Word 11 Invalid                           True                      
        Word 12 Invalid                           False                      
        Word 13 Invalid                           False                      
        Word 14 Invalid                           False                      
        Word 15 Invalid                           False                      
        Word 16 Invalid                           False                      
    PF Invalidity Word 2                                                            (0x000000FE)
        Word 17 Invalid                           False                      
        Word 18 Invalid                           False                      
        Word 19 Invalid                           False                      
        Word 20 Invalid                           False                      
        Word 21 Invalid                           False                      
        Word 22 Invalid                           False                      
        Word 23 Invalid                           False                      
        Word 24 Invalid                           False                      
        Word 25 Invalid                           False                      
        Word 26 Invalid                           False                      
        Word 27 Invalid                           False                      
        Word 28 Invalid                           False                      
        Word 29 Invalid                           False                      
        Word 30 Invalid                           False                      
    PF TGT ID                                     1                                 (0x00000100)
    Fuze Mode Selection                                                             (0x00000108)
        Func at Impact                            True                      
        Func on Time Aft Impact                   False                      
        Func on Proximity                         False                      
        Long Delay Enable                         False                      
    Arm Time                                                                        (0x0000010A)
        Integer                                   +  305  microsec            
        Exponent                                  +  4                      
    Time From Impact                                                                (0x0000010E)
        Integer                                   +    0  microsec            
        Exponent                                  +  0                      
    Fuze Function Distance                        + 00000.0  meters                 (0x00000110)
    Void Number                                   0                                 (0x0000011C)
    PF Checksum                                   9880                              (0x00000134)
    IZ Entry                                      - 27979.0020  feet                (0x00000148)
    IZ Exit                                       - 15328.0840  feet                (0x0000014C)
    IZ TOF                                        + 037.5000  sec                   (0x00000150)
    IR Entry                                      - 48871.3906  feet                (0x00000154)
    IR Exit                                       - 18372.7031  feet                (0x00000158)
    IR TOF                                        + 037.5000  sec                   (0x0000015C)
    IZ Down RNG Ref Point                         - 21784.7773  feet                (0x00000160)
    IZ Cross RNG Ref Point                        + 472.4409  feet                  (0x00000164)
    IZ Polygon Radii 0                            + 6771.6533  feet                 (0x00000168)
    IZ Polygon Radii 40                           + 7086.6143  feet                 (0x0000016C)
    IZ Polygon Radii 80                           + 7559.0552  feet                 (0x00000170)
    IZ Polygon Radii 120                          + 7716.5356  feet                 (0x00000174)
    IZ Polygon Radii 160                          + 6876.6406  feet                 (0x00000178)
    IZ Polygon Radii 200                          + 7034.1206  feet                 (0x0000017C)
    IZ Polygon Radii 240                          + 7559.0552  feet                 (0x00000180)
    IZ Polygon Radii 280                          + 7559.0552  feet                 (0x00000184)
    IZ Polygon Radii 320                          + 7139.1074  feet                 (0x00000188)
    IR Down RNG Ref Point                         - 33438.3203  feet                (0x0000018C)
    IR Cross RNG Ref Point                        + 209.9738  feet                  (0x00000190)
    IR Polygon Radii 0                            + 15958.0049  feet                (0x00000194)
    IR Polygon Radii 40                           + 16850.3945  feet                (0x00000198)
    IR Polygon Radii 80                           + 16587.9258  feet                (0x0000019C)
    IR Polygon Radii 120                          + 15800.5254  feet                (0x000001A0)
    IR Polygon Radii 160                          + 15695.5381  feet                (0x000001A4)
    IR Polygon Radii 200                          + 16797.9004  feet                (0x000001A8)
    IR Polygon Radii 240                          + 16535.4336  feet                (0x000001AC)
    IR Polygon Radii 280                          + 15800.5254  feet                (0x000001B0)
    IR Polygon Radii 320                          + 15905.5117  feet                (0x000001B4)
    Radar Altitude                                + 3888.0000  feet                 (0x000001B8)
    Prime Windspeed North                         - 001.2461  ft/sec                (0x000001BC)
    Prime Windspeed East                          + 059.6609  ft/sec                (0x000001C0)
    Static Pressure PSF                           + 804.2331  lbs/ft2               (0x000001C4)
    True Mach                                       000.6389  mach                  (0x000001C8)
    Freestream Air TEMP Rankine                   + 454.5468  deg R                 (0x000001CC)
    Radar Altimeter Status Flags                                                    (0x000001D0)
        RA Parity Error                           False                      
        Invalid                                   True                      
        Altitude Invalid                          True                      
        Self Test                                 False                      
        Failure Monitor                           True                      
        Air Data Valid                            True                      
        Air Data Nogo                             False                      
        Operator Entered Air Speed                False                      
    Store Description                             GBU-31V1        OGB427            (0x000001D1)
    Operator Modified OAT                         0                                 (0x000001E7)
    TGP LOS Latitude At Release                   N 000:00.0000  deg                (0x000001E8)
    TGP LOS Longitude At Release                  E 0000:00.0000  deg               (0x000001F0)
    TGP LOS Elev At Release                       +    0  feet                      (0x000001F8)
    TGP LOS Latency                               + 0000.0000  sec                  (0x00000200)
    TGP Mode                                      Static                            (0x00000204)
    SPI Id                                                                          (0x00000206)
        Radar slaved to TGP                       False                      
        TGP slaved to radar                       False                      
        Send target operation                     False                      
        Stream operation                          False                      
        Send SPI operation                        False                      
        LOS Invalid - TGP COMM                    False                      
        LOS Invalid - Unreasonable Data           False                      
        LOS Invalid - Video Blocked               False                      
        LOS SPI Quality                           Unknown Quality                      
        LOS Tracking Mode                         None                      
        TGP Sub_Mode CMDed                        False                      
        Slew CMD Validity                         False                      
    IU 1553A Status                                                                 (0x00000208)
        Remote Term Address                       0                      
        Message Error                             False                      
        Instrumentation                           False                      
        Service Req                               False                      
        Broadcast RCVD                            False                      
        Busy                                      False                      
        Subsys Failure                            False                      
        Dynamic Control                           False                      
        Remote Term Failure                       False                      
    Max TQV                                       0                                 (0x0000020C)
    LTQV                                          + 00000.00  feet                  (0x00000210)
    TQV                                           + 00000.00  feet                  (0x00000218)
    TGT GND Track At Release                      + 000.0000000  deg                (0x00000220)
    TGT GND Speed At Release                        00000.00  ft/sec                (0x00000228)
    TGT Vertical Vel At Release                     00000.00  ft/sec                (0x00000230)

"""

print('Parsing Releases...')

debug = True

record = Group(Literal("Record Number") + Word(nums)) + Suppress(Literal("Weapon Scoring") + lineEnd())
msnEventExpanded = Suppress(Group(Literal("Launch") + LineEnd())) | Suppress(
    Group(Literal("Gravity Weapon Scoring") + LineEnd())) | Suppress(Group(Literal("Weapon Launch") + LineEnd()))
eventKey = SkipTo(": ")
# Improve?
eventValue = SkipTo(lineEnd)
eventData = NotAny("Launch") + NotAny("Gravity Weapon Scoring") + NotAny("Weapon Launch") + NotAny('Weapon Jettison') + Group(
    eventKey + Suppress(":") + eventValue) + Suppress(lineEnd())
recordBlock = record + OneOrMore(eventData) + msnEventExpanded

pData = Suppress(Literal("PERTINENT DATA"))
SPACE_CHARS = ' \t'
dataField = CharsNotIn(SPACE_CHARS)
space = Word(SPACE_CHARS, exact=1) ^ Word(SPACE_CHARS, exact=2) ^ Word(SPACE_CHARS, exact=3) ^ Word(SPACE_CHARS,exact=4) ^ Word(SPACE_CHARS, exact=5) #^ Word(SPACE_CHARS, exact=8)
dataKey = delimitedList(dataField, delim=space, combine=True)
dataValue = Combine(dataField + ZeroOrMore(space + dataField))

spaceAlternate = Word(SPACE_CHARS, exact=8) ^ Word(SPACE_CHARS, exact=12)
dataValueStoreDescription = Combine(dataField + ZeroOrMore(spaceAlternate))

dataBlock = Group(dataKey + dataValue) + Optional(Suppress("(" + Word(alphanums) + ")")) + Suppress(
    LineEnd()) | Group(dataKey + Suppress("(") + Word(alphanums) + Suppress(")")) + Suppress(LineEnd()) | Group(
    dataKey + dataValue) + Suppress(LineEnd()) | Group(Literal("Store Description") + dataValueStoreDescription) + Suppress(Word(alphanums) + "(" + Word(alphanums) + ")" +LineEnd())

name_parser = Dict(recordBlock + pData + OneOrMore(dataBlock))

config.count = 0

config.jdam = []
config.gwd = []
config.wcmd = []
config.jassm = []
config.mald = []

if debug:
    for obj, start, end in name_parser.scanString(texttest):
        print(obj.asDict())
        if obj['Application ID'] == '13':
            obj.pop("TGTING Data", None)
            jdamparse(obj)
            config.jdam.append(obj)
            print(obj.asDict())
        if obj['Application ID'] == '1':
            gwdparse(obj)
            config.gwd.append(obj)
            print(obj.asDict())
        if obj['Application ID'] == '7':
            wcmdparse(obj)
            config.wcmd.append(obj)
            print(obj.asDict())
        if obj['Application ID'] == '9':
            jassmparse(obj)
            config.jassm.append(obj)
            print(obj.asDict())
        if obj['Application ID'] == '12':
            maldparse(obj)
            config.mald.append(obj)
            print(obj.asDict())
        config.count += 1
else:
    for obj, start, end in name_parser.scanString(config.msnData):
        currentWPN = obj.asDict()
        if obj['Application ID'] == '13':
            obj.pop("TGTING Data", None)
            jdamparse(obj)
            currentWPN = obj.asDict()
            currentWPN['wpn'] = 'JDAM'
            config.jdam.append(currentWPN)
        if obj['Application ID'] == '1':
            gwdparse(obj)
            obj.append(['wpn', 'gwd'])
            currentWPN = obj.asDict()
            currentWPN['wpn'] = 'GWD'
            config.gwd.append(currentWPN)
        if obj['Application ID'] == '7':
            wcmdparse(obj)
            obj.append(['wpn', 'wcmd'])
            currentWPN = obj.asDict()
            currentWPN['wpn'] = 'WCMD'
            config.wcmd.append(currentWPN)
        if obj['Application ID'] == '9':
            jassmparse(obj)
            obj.append(['wpn', 'jassm'])
            currentWPN = obj.asDict()
            currentWPN['wpn'] = 'JASSM'
            config.jassm.append(currentWPN)
        if obj['Application ID'] == '12':
            maldparse(obj)
            obj.append(['wpn', 'mald'])
            currentWPN = obj.asDict()
            currentWPN['wpn'] = 'MALD'
            config.mald.append(currentWPN)
        config.count += 1
    print('\rReleases Found: ' + str(config.count))
    config.releases_available.set()