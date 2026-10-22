import Foundation
import UserNotifications

let center = UNUserNotificationCenter.current()
let arguments = CommandLine.arguments
let statusOnly = arguments.count > 1 && arguments[1] == "--status"

func finish(_ code: Int32) {
    fflush(stdout)
    exit(code)
}

center.getNotificationSettings { settings in
    if statusOnly {
        switch settings.authorizationStatus {
        case .authorized, .provisional: print("authorized")
        case .denied: print("disabled")
        case .notDetermined: print("not-determined")
        @unknown default: print("unknown")
        }
        finish(0)
    }
    guard arguments.count == 3 else { finish(2); return }
    center.requestAuthorization(options: [.alert, .sound]) { granted, error in
        guard granted && error == nil else { finish(1); return }
        let content = UNMutableNotificationContent()
        content.title = arguments[1]
        content.body = arguments[2]
        content.sound = .default
        let request = UNNotificationRequest(identifier: UUID().uuidString,
                                            content: content, trigger: nil)
        center.add(request) { error in
            finish(error == nil ? 0 : 1)
        }
    }
}
RunLoop.main.run()
