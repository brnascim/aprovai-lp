import XCTest
@testable import ADBCore

final class RemoteCommandTests: XCTestCase {

    func testKeyEventCodesMatchAndroidKeyEvent() {
        XCTAssertEqual(RemoteCommand.keyEvent(.dpadCenter), "input keyevent 23")
        XCTAssertEqual(RemoteCommand.keyEvent(.back), "input keyevent 4")
        XCTAssertEqual(RemoteCommand.keyEvent(.home), "input keyevent 3")
        XCTAssertEqual(RemoteCommand.keyEvent(.power), "input keyevent 26")
        XCTAssertEqual(RemoteCommand.keyEvent(.volumeUp), "input keyevent 24")
        XCTAssertEqual(RemoteCommand.keyEvent(.mute), "input keyevent 164")
        XCTAssertEqual(RemoteCommand.keyEvent(.mediaPlayPause), "input keyevent 85")
        XCTAssertEqual(RemoteCommand.keyEvent(.appSwitch), "input keyevent 187")
    }

    func testDigitMapping() {
        XCTAssertEqual(AndroidKey.digit(0), .num0)
        XCTAssertEqual(AndroidKey.digit(9), .num9)
        XCTAssertEqual(AndroidKey.digit(0)?.rawValue, 7)
        XCTAssertEqual(AndroidKey.digit(9)?.rawValue, 16)
        XCTAssertNil(AndroidKey.digit(10))
        XCTAssertNil(AndroidKey.digit(-1))
    }

    func testTapAndSwipe() {
        XCTAssertEqual(RemoteCommand.tap(x: 960, y: 540), "input tap 960 540")
        XCTAssertEqual(
            RemoteCommand.swipe(fromX: 100, fromY: 200, toX: 300, toY: 400, durationMS: 150),
            "input swipe 100 200 300 400 150"
        )
        // Zero/negative duration is clamped to something valid.
        XCTAssertEqual(
            RemoteCommand.swipe(fromX: 0, fromY: 0, toX: 1, toY: 1, durationMS: 0),
            "input swipe 0 0 1 1 1"
        )
    }

    func testTextEscapesSpacesAndQuotes() {
        XCTAssertEqual(RemoteCommand.text("hello"), "input text 'hello'")
        XCTAssertEqual(RemoteCommand.text("hello world"), "input text 'hello%sworld'")
        XCTAssertEqual(RemoteCommand.text("it's"), "input text 'it'\\''s'")
        XCTAssertEqual(RemoteCommand.text("a\nb"), "input text 'a%sb'")
    }

    func testParseWmSizePhysical() {
        let output = "Physical size: 1920x1080\n"
        XCTAssertEqual(RemoteCommand.parseWmSize(output)?.width, 1920)
        XCTAssertEqual(RemoteCommand.parseWmSize(output)?.height, 1080)
    }

    func testParseWmSizePrefersOverride() {
        let output = "Physical size: 1920x1080\nOverride size: 1280x720\n"
        let parsed = RemoteCommand.parseWmSize(output)
        XCTAssertEqual(parsed?.width, 1280)
        XCTAssertEqual(parsed?.height, 720)
    }

    func testParseWmSizeGarbageReturnsNil() {
        XCTAssertNil(RemoteCommand.parseWmSize(""))
        XCTAssertNil(RemoteCommand.parseWmSize("error: no display"))
        XCTAssertNil(RemoteCommand.parseWmSize("Physical size: 0x0"))
    }

    func testLaunchPackage() {
        XCTAssertEqual(
            RemoteCommand.launchPackage("com.google.android.youtube"),
            "monkey -p com.google.android.youtube -c android.intent.category.LAUNCHER 1"
        )
    }
}
