// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "ADBCore",
    platforms: [
        .iOS(.v16),
        .macOS(.v13)
    ],
    products: [
        .library(name: "ADBCore", targets: ["ADBCore"])
    ],
    targets: [
        .target(
            name: "ADBCore",
            path: "Sources/ADBCore"
        ),
        .testTarget(
            name: "ADBCoreTests",
            dependencies: ["ADBCore"],
            path: "Tests/ADBCoreTests"
        )
    ]
)
