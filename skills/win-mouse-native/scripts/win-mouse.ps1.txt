$ErrorActionPreference = 'Stop'

# Avoid PowerShell parameter binding so negative numbers like -5 work.
$Cmd = $args[0]
$A = $args[1]
$B = $args[2]

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class WinMouse {
  [StructLayout(LayoutKind.Sequential)]
  public struct POINT { public int X; public int Y; }

  [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT lpPoint);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);

  [StructLayout(LayoutKind.Sequential)]
  public struct INPUT {
    public uint type;
    public MOUSEINPUT mi;
  }

  [StructLayout(LayoutKind.Sequential)]
  public struct MOUSEINPUT {
    public int dx;
    public int dy;
    public uint mouseData;
    public uint dwFlags;
    public uint time;
    public IntPtr dwExtraInfo;
  }

  [DllImport("user32.dll", SetLastError=true)]
  public static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

  public const uint INPUT_MOUSE = 0;

  public const uint MOUSEEVENTF_MOVE = 0x0001;
  public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
  public const uint MOUSEEVENTF_LEFTUP = 0x0004;
  public const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
  public const uint MOUSEEVENTF_RIGHTUP = 0x0010;
  public const uint MOUSEEVENTF_MIDDLEDOWN = 0x0020;
  public const uint MOUSEEVENTF_MIDDLEUP = 0x0040;

  public static POINT GetPos() {
    POINT p; GetCursorPos(out p); return p;
  }

  public static void Button(string btn, string action) {
    uint flag;
    switch(btn.ToLowerInvariant()) {
      case "left":   flag = (action=="down") ? MOUSEEVENTF_LEFTDOWN : MOUSEEVENTF_LEFTUP; break;
      case "right":  flag = (action=="down") ? MOUSEEVENTF_RIGHTDOWN : MOUSEEVENTF_RIGHTUP; break;
      case "middle": flag = (action=="down") ? MOUSEEVENTF_MIDDLEDOWN : MOUSEEVENTF_MIDDLEUP; break;
      default: throw new ArgumentException("button must be left|right|middle");
    }

    var input = new INPUT();
    input.type = INPUT_MOUSE;
    input.mi = new MOUSEINPUT(){ dx=0, dy=0, mouseData=0, dwFlags=flag, time=0, dwExtraInfo=IntPtr.Zero };

    var arr = new INPUT[]{ input };
    var sent = SendInput(1, arr, Marshal.SizeOf(typeof(INPUT)));
    if(sent != 1) throw new Exception("SendInput failed: " + Marshal.GetLastWin32Error());
  }

  public static void Click(string btn) {
    Button(btn, "down");
    Button(btn, "up");
  }
}
"@ -Language CSharp

function JsonOut($ok, $cmd, $details) {
  $obj = [ordered]@{ ok = $ok; cmd = $cmd }
  foreach($k in $details.Keys){ $obj[$k] = $details[$k] }
  ($obj | ConvertTo-Json -Compress)
}

if(-not $Cmd){
  Write-Output (JsonOut $false $null @{ error = 'usage: win-mouse <move|abs|click|down|up> ...' })
  exit 2
}

$before = [WinMouse]::GetPos()

switch($Cmd.ToLowerInvariant()){
  'move' {
    if($null -eq $A -or $null -eq $B){ throw 'usage: win-mouse move <dx> <dy>' }
    $dx = [int]$A; $dy = [int]$B
    $x = $before.X + $dx
    $y = $before.Y + $dy
    [void][WinMouse]::SetCursorPos($x,$y)
    $after = [WinMouse]::GetPos()
    Write-Output (JsonOut $true 'move' @{ before=$before; after=$after; dx=$dx; dy=$dy })
  }
  'abs' {
    if($null -eq $A -or $null -eq $B){ throw 'usage: win-mouse abs <x> <y>' }
    $x = [int]$A; $y = [int]$B
    [void][WinMouse]::SetCursorPos($x,$y)
    $after = [WinMouse]::GetPos()
    Write-Output (JsonOut $true 'abs' @{ before=$before; after=$after; x=$x; y=$y })
  }
  'click' {
    $btn = if($A){$A}else{'left'}
    [WinMouse]::Click($btn)
    $after = [WinMouse]::GetPos()
    Write-Output (JsonOut $true 'click' @{ button=$btn; before=$before; after=$after })
  }
  'down' {
    if(-not $A){ throw 'usage: win-mouse down <left|right|middle>' }
    [WinMouse]::Button($A,'down')
    $after = [WinMouse]::GetPos()
    Write-Output (JsonOut $true 'down' @{ button=$A; before=$before; after=$after })
  }
  'up' {
    if(-not $A){ throw 'usage: win-mouse up <left|right|middle>' }
    [WinMouse]::Button($A,'up')
    $after = [WinMouse]::GetPos()
    Write-Output (JsonOut $true 'up' @{ button=$A; before=$before; after=$after })
  }
  default {
    Write-Output (JsonOut $false $Cmd @{ error = 'unknown command' })
    exit 2
  }
}
