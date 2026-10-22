#define AppVersion "0.1.0"
[Setup]
AppId={{CE34877C-0491-482A-88A7-ACED44DA801D}
AppName=QuickMD
AppVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\QuickMD
DefaultGroupName=QuickMD
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\..\dist
OutputBaseFilename=QuickMD-Setup-Windows-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ChangesEnvironment=yes
CloseApplications=yes
RestartApplications=no
UninstallDisplayIcon={app}\quickmd.exe
LicenseFile=..\..\LICENSE
#ifdef SignedBuild
SignTool=QuickMD
SignedUninstaller=yes
#endif

[Files]
Source: "..\..\dist\QuickMD\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\QuickMD"; Filename: "{app}\quickmd.exe"; Parameters: "doctor"; AppUserModelID: "QuickMD.Desktop"

[Registry]
Root: HKCU; Subkey: "Software\Classes\AppUserModelId\QuickMD.Desktop"; ValueType: string; ValueName: "DisplayName"; ValueData: "QuickMD"; Flags: uninsdeletekey

[UninstallRun]
Filename: "{app}\quickmd.exe"; Parameters: "unintegrate"; Flags: runhidden waituntilterminated; RunOnceId: "QuickMD.Unintegrate"

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\QuickMD\Data\logs"; Check: ShouldPurgeLogs
Type: filesandordirs; Name: "{localappdata}\QuickMD\Data\queue"

[Code]
function ShouldPurgeLogs(): Boolean;
begin
  Result := ExpandConstant('{param:PURGELOGS|0}') = '1';
end;

function HasPath(Value, Item: String): Boolean;
begin
  Result := Pos(';' + Lowercase(Item) + ';', ';' + Lowercase(Value) + ';') > 0;
end;

procedure AddUserPath();
var Value, Item: String;
begin
  Item := ExpandConstant('{app}');
  RegQueryStringValue(HKCU, 'Environment', 'Path', Value);
  if not HasPath(Value, Item) then begin
    if (Value <> '') and (Copy(Value, Length(Value), 1) <> ';') then Value := Value + ';';
    RegWriteExpandStringValue(HKCU, 'Environment', 'Path', Value + Item);
    RegWriteDWordValue(HKCU, 'Software\QuickMD', 'PathOwned', 1);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var Code: Integer;
begin
  if CurStep = ssPostInstall then begin
    if not Exec(ExpandConstant('{app}\quickmd.exe'), 'integrate', '', SW_HIDE, ewWaitUntilTerminated, Code) then
      RaiseException('QuickMD menu registration could not start. Run quickmd repair.');
    if Code <> 0 then RaiseException('QuickMD menu registration failed. Run quickmd repair.');
    if not Exec(ExpandConstant('{app}\quickmd.exe'), 'doctor', '', SW_HIDE, ewWaitUntilTerminated, Code) then
      RaiseException('QuickMD diagnostics could not start.');
    if Code <> 0 then RaiseException('QuickMD diagnostics failed. Check install logs.');
    AddUserPath();
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var Value, Item, Token, NewValue: String; I: Integer; Owned: Cardinal;
begin
  if CurUninstallStep = usPostUninstall then begin
    if RegQueryDWordValue(HKCU, 'Software\QuickMD', 'PathOwned', Owned) and (Owned = 1) then begin
      Item := ExpandConstant('{app}');
      RegQueryStringValue(HKCU, 'Environment', 'Path', Value);
      NewValue := '';
      while Value <> '' do begin
        I := Pos(';', Value);
        if I = 0 then I := Length(Value) + 1;
        Token := Copy(Value, 1, I - 1);
        Delete(Value, 1, I);
        if Lowercase(Token) <> Lowercase(Item) then begin
          if NewValue <> '' then NewValue := NewValue + ';';
          NewValue := NewValue + Token;
        end;
      end;
      RegWriteExpandStringValue(HKCU, 'Environment', 'Path', NewValue);
    end;
    RegDeleteValue(HKCU, 'Software\QuickMD', 'PathOwned');
    RegDeleteKeyIfEmpty(HKCU, 'Software\QuickMD');
  end;
end;
