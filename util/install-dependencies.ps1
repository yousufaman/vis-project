# Install basic tools
winget install --source winget `
     Git.Git `
     Python.Python.3.13 `
     Kitware.CMake `
     Microsoft.VisualStudioCode

# Detect architecture and install matching MSVC Build Tools
$arch = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture

switch ($arch) {
    "Arm64" { $component = "Microsoft.VisualStudio.Component.VC.Tools.ARM64" }
    "X64"   { $component = "Microsoft.VisualStudio.Component.VC.Tools.x86.x64" }
    "X86"   { $component = "Microsoft.VisualStudio.Component.VC.Tools.x86.x64" }
    default { Write-Error "Unsupported architecture: $arch"; exit 1 }
}

$sdk  = "Microsoft.VisualStudio.Workload.VCTools"

winget install --source winget `
    Microsoft.VisualStudio.2022.BuildTools `
    --force `
    --override "--wait --passive --add $component --add $sdk --includeRecommended"


