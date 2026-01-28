; installer.iss - Inno Setup script
[Setup]
AppName=Auto Subtitle Generator
AppVersion=1.0
DefaultDirName={pf}\Auto Subtitle Generator
DefaultGroupName=Auto Subtitle Generator
OutputDir=dist_installer
OutputBaseFilename=AutoSubtitleSetup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
DisableWelcomePage=no

[Files]
Source: "F:\project 2"; DestDir: "{app}"; Flags: ignoreversion
; Optional icon
; Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Auto Subtitle Generator"; Filename: "{app}\main.exe"
Name: "{group}\Uninstall Auto Subtitle Generator"; Filename: "{uninstallexe}"
Name: "{userdesktop}\Auto Subtitle Generator"; Filename: "{app}\main.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: checkedonce

[Run]
Filename: "{app}\main.exe"; Description: "Launch Auto Subtitle Generator"; Flags: nowait postinstall skipifsilent
