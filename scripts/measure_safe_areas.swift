// Superseded the earlier draft (SwiftUI onAppear, portrait only, manual rotation). Canonical copy: scripts/simulator/Measure.swift; runner: scripts/simulator/run_all.sh.
// Screen-spec probe app for Xcode Simulator (scene-based UIKit app, built with swiftc).
// Logs UIScreen bounds/nativeBounds/scale/nativeScale, window safe-area insets in portrait,
// landscape-left and landscape-right (rotated with UIWindowScene.requestGeometryUpdate),
// status bar height, home-indicator presence, UIScreen.screens / connected scenes, and the
// private UIScreen _displayCornerRadius (UNOFFICIAL). Output: stdout line "SSM_JSON <json>"
// and Documents/measure.json in the app's data container.
// Build + run: see scripts/simulator/run_all.sh
import UIKit

func ins(_ i: UIEdgeInsets) -> [String: Double] { ["top": i.top, "left": i.left, "bottom": i.bottom, "right": i.right] }
func sz(_ r: CGRect) -> [String: Double] { ["x": r.origin.x, "y": r.origin.y, "width": r.width, "height": r.height] }
func orientName(_ o: UIInterfaceOrientation) -> String {
    switch o { case .portrait: return "portrait"; case .portraitUpsideDown: return "portraitUpsideDown"
    case .landscapeLeft: return "landscapeLeft"; case .landscapeRight: return "landscapeRight"; default: return "unknown" }
}
func screenInfo(_ s: UIScreen) -> [String: Any] {
    var d: [String: Any] = ["bounds_pt": sz(s.bounds), "native_bounds_px": sz(s.nativeBounds), "scale": s.scale,
                            "native_scale": s.nativeScale, "max_fps": s.maximumFramesPerSecond, "is_main": s === UIScreen.main]
    let sel = NSSelectorFromString("_displayCornerRadius")
    if s.responds(to: sel), let v = s.value(forKey: "_displayCornerRadius") as? NSNumber {
        d["display_corner_radius_unofficial"] = v.doubleValue
    } else { d["display_corner_radius_unofficial"] = NSNull() }
    return d
}

var results: [String: Any] = [:]
var startedMeasuring = false

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool { true }
    func application(_ application: UIApplication, configurationForConnecting s: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        var roles = (results["scene_roles_requested"] as? [String]) ?? []
        roles.append(s.role.rawValue); results["scene_roles_requested"] = roles
        let c = UISceneConfiguration(name: nil, sessionRole: s.role)
        c.delegateClass = SceneDelegate.self
        return c
    }
}

class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?
    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options: UIScene.ConnectionOptions) {
        guard let ws = scene as? UIWindowScene else { return }
        let w = UIWindow(windowScene: ws)
        let vc = MeasureVC()
        vc.isPrimary = session.role == .windowApplication && !startedMeasuring
        if vc.isPrimary { startedMeasuring = true }
        w.rootViewController = vc
        w.makeKeyAndVisible()
        window = w
    }
}

class MeasureVC: UIViewController {
    var isPrimary = false
    var allowed: UIInterfaceOrientationMask = .all
    var ran = false
    override var supportedInterfaceOrientations: UIInterfaceOrientationMask { allowed }
    override func viewDidLoad() { super.viewDidLoad(); view.backgroundColor = .systemTeal }
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        guard isPrimary, !ran else { return }
        ran = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { self.run() }
    }
    func snapshot() -> [String: Any] {
        guard let w = view.window, let ws = w.windowScene else { return ["error": "no window"] }
        let sb = ws.statusBarManager
        return ["interface_orientation": orientName(ws.interfaceOrientation),
                "window_bounds_pt": sz(w.bounds), "window_frame_pt": sz(w.frame),
                "window_safe_area_insets_pt": ins(w.safeAreaInsets),
                "view_safe_area_insets_pt": ins(view.safeAreaInsets),
                "status_bar_frame_pt": sz(sb?.statusBarFrame ?? .zero),
                "status_bar_height_pt": sb?.statusBarFrame.height ?? -1,
                "status_bar_hidden": sb?.isStatusBarHidden ?? false,
                "home_indicator_present": w.safeAreaInsets.bottom > 0,
                "screen_bounds_pt": sz(ws.screen.bounds),
                "uiscreen_main_bounds_pt": sz(UIScreen.main.bounds),
                "trait_display_scale": traitCollection.displayScale]
    }
    func rotate(_ mask: UIInterfaceOrientationMask, _ key: String, then: @escaping () -> Void) {
        guard let ws = view.window?.windowScene else { then(); return }
        allowed = mask
        setNeedsUpdateOfSupportedInterfaceOrientations()
        ws.requestGeometryUpdate(.iOS(interfaceOrientations: mask)) { err in
            results["\(key)_geometry_error"] = err.localizedDescription
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) {
            self.view.window?.layoutIfNeeded()
            results[key] = self.snapshot(); then()
        }
    }
    func run() {
        let env = ProcessInfo.processInfo.environment
        results["simulator_model_identifier"] = env["SIMULATOR_MODEL_IDENTIFIER"] ?? NSNull()
        results["simulator_device_name"] = env["SIMULATOR_DEVICE_NAME"] ?? NSNull()
        results["simulator_runtime_version"] = env["SIMULATOR_RUNTIME_VERSION"] ?? NSNull()
        results["simulator_runtime_build"] = env["SIMULATOR_RUNTIME_BUILD_VERSION"] ?? NSNull()
        results["system_version"] = UIDevice.current.systemVersion
        results["idiom"] = UIDevice.current.userInterfaceIdiom == .pad ? "pad" : (UIDevice.current.userInterfaceIdiom == .phone ? "phone" : "other")
        results["main_screen"] = screenInfo(UIScreen.main)
        results["uiscreen_screens"] = UIScreen.screens.map(screenInfo)
        results["launch"] = snapshot()
        rotate(.portrait, "portrait") {
            self.rotate(.landscapeLeft, "landscape_left") {
                self.rotate(.landscapeRight, "landscape_right") {
                    self.rotate(.portrait, "portrait_after") { self.finish() }
                }
            }
        }
    }
    func finish() {
        results["connected_scenes"] = UIApplication.shared.connectedScenes.compactMap { s -> [String: Any]? in
            guard let ws = s as? UIWindowScene else { return nil }
            return ["role": ws.session.role.rawValue, "screen": screenInfo(ws.screen),
                    "windows": ws.windows.map { ["frame_pt": sz($0.frame), "safe_area_insets_pt": ins($0.safeAreaInsets)] }]
        }
        results["uiscreen_screens_at_end"] = UIScreen.screens.map(screenInfo)
        let data = try! JSONSerialization.data(withJSONObject: results, options: [.sortedKeys])
        let url = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("measure.json")
        try? data.write(to: url)
        print("SSM_JSON " + String(data: data, encoding: .utf8)!)
        fflush(stdout)
    }
}
