import SwiftUI

@main
struct BackgroundRemovalApp: App {
    @StateObject private var setup = SetupManager()

    var body: some Scene {
        WindowGroup {
            SetupView(setup: setup)
                .frame(width: 520, height: 380)
        }
        .windowResizability(.contentSize)
    }
}

final class SetupManager: ObservableObject {
    @Published var state: State = .ready
    @Published var message = "Background Removal is ready to set up."
    @Published var progress = 0.0

    enum State {
        case ready, running, complete, failed
    }

    func start() {
        guard state != .running else { return }
        state = .running
        progress = 0.05
        message = "Preparing Background Removal…"

        DispatchQueue.global(qos: .userInitiated).async {
            do {
                try self.runSetup()
                DispatchQueue.main.async {
                    self.progress = 1
                    self.message = "Setup complete. Background Removal is ready in Finder."
                    self.state = .complete
                }
            } catch {
                DispatchQueue.main.async {
                    self.message = error.localizedDescription
                    self.state = .failed
                }
            }
        }
    }

    private func runSetup() throws {
        guard ProcessInfo.processInfo.operatingSystemVersion.majorVersion >= 10 else {
            throw SetupError.message("This version of macOS is not supported.")
        }

        let appSupport = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Library/Application Support/Background Removal", isDirectory: true)
        try FileManager.default.createDirectory(at: appSupport, withIntermediateDirectories: true)

        DispatchQueue.main.async { self.progress = 0.2; self.message = "Installing the local processing environment…" }
        try runBundledScript(named: "setup-runtime", arguments: [appSupport.path])

        DispatchQueue.main.async { self.progress = 0.8; self.message = "Installing the Finder Quick Action…" }
        try runBundledScript(named: "install-quick-action", arguments: [appSupport.path])
    }

    private func runBundledScript(named name: String, arguments: [String]) throws {
        guard let url = Bundle.main.url(forResource: name, withExtension: "command") else {
            throw SetupError.message("The setup component \(name) is missing from the application.")
        }
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/bin/zsh")
        process.arguments = [url.path] + arguments
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe
        try process.run()
        process.waitUntilExit()
        if process.terminationStatus != 0 {
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            let output = String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines)
            throw SetupError.message(output?.isEmpty == false ? output! : "Setup could not be completed.")
        }
    }

    enum SetupError: LocalizedError {
        case message(String)
        var errorDescription: String? {
            switch self { case .message(let text): return text }
        }
    }
}

struct SetupView: View {
    @ObservedObject var setup: SetupManager

    var body: some View {
        VStack(spacing: 22) {
            Image(systemName: setup.state == .complete ? "checkmark.circle.fill" : "wand.and.stars")
                .font(.system(size: 54))

            VStack(spacing: 8) {
                Text(setup.state == .complete ? "You're ready" : "Set up Background Removal")
                    .font(.system(size: 28, weight: .semibold))
                Text(setup.message)
                    .multilineTextAlignment(.center)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: 410)
            }

            if setup.state == .running {
                ProgressView(value: setup.progress)
                    .frame(width: 360)
            }

            if setup.state == .ready || setup.state == .failed {
                Button(setup.state == .failed ? "Try Again" : "Set Up") {
                    setup.start()
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
            } else if setup.state == .complete {
                Text("Select an image in Finder, right-click it, and choose Quick Actions → Remove Background.")
                    .font(.callout)
                    .multilineTextAlignment(.center)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: 390)
            }
        }
        .padding(42)
    }
}
