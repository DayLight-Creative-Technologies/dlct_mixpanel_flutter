// swift-tools-version: 5.6
import PackageDescription

let package = Package(
    name: "mixpanel_flutter",
    platforms: [
        .iOS("15.0")
    ],
    products: [
        .library(
            name: "mixpanel-flutter",
            targets: ["mixpanel_flutter"]
        )
    ],
    dependencies: [
        // DLCT fork: optOutTracking() discards the unsent event queue (SocialScoreKeeper FUNNEL-2026-001
        // REQ-030). Pinned by revision to the commit SocialScoreKeeper's ios/Podfile.lock pins.
        .package(
            url: "https://github.com/DayLight-Creative-Technologies/dlct_mixpanel_swift.git",
            revision: "dd63aa5d4329c90eebf56ace320446c3e086f214"
        ),
        .package(name: "FlutterFramework", path: "../FlutterFramework")
    ],
    targets: [
        .target(
            name: "mixpanel_flutter",
            dependencies: [
                .product(name: "Mixpanel", package: "dlct_mixpanel_swift"),
                .product(name: "FlutterFramework", package: "FlutterFramework")
            ],
            path: "Sources/mixpanel_flutter",
            resources: []
        )
    ]
)
