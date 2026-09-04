import Foundation
import UniformTypeIdentifiers

@objc(FinderAction)
final class FinderAction: NSObject, NSExtensionRequestHandling {
    func beginRequest(with context: NSExtensionContext) {
        let items = context.inputItems.compactMap { $0 as? NSExtensionItem }
        let providers = items.flatMap { $0.attachments ?? [] }
        let imageType = UTType.image.identifier

        let group = DispatchGroup()
        var urls: [URL] = []
        let lock = NSLock()

        for provider in providers where provider.hasItemConformingToTypeIdentifier(imageType) {
            group.enter()
            provider.loadFileRepresentation(forTypeIdentifier: imageType) { url, _ in
                defer { group.leave() }
                guard let url else { return }
                lock.lock()
                urls.append(url)
                lock.unlock()
            }
        }

        group.notify(queue: .global(qos: .userInitiated)) {
            let runtime = FileManager.default.homeDirectoryForCurrentUser
                .appendingPathComponent("Library/Application Support/Background Removal/runtime")
            let python = runtime.appendingPathComponent("venv/bin/python3")
            let script = runtime.appendingPathComponent("remove_bg.py")

            guard FileManager.default.isExecutableFile(atPath: python.path),
                  FileManager.default.fileExists(atPath: script.path) else {
                self.complete(context, message: "Background Removal needs to be set up first.")
                return
            }

            let process = Process()
            process.executableURL = python
            process.arguments = [script.path] + urls.map(\.path)
            process.standardOutput = FileHandle.nullDevice
            process.standardError = FileHandle.nullDevice

            do {
                try process.run()
                process.waitUntilExit()
                self.complete(context, message: process.terminationStatus == 0 ? nil : "Some images could not be processed.")
            } catch {
                self.complete(context, message: error.localizedDescription)
            }
        }
    }

    private func complete(_ context: NSExtensionContext, message: String?) {
        if let message {
            let item = NSExtensionItem()
            item.attributedContentText = NSAttributedString(string: message)
            context.completeRequest(returningItems: [item], completionHandler: nil)
        } else {
            context.completeRequest(returningItems: nil, completionHandler: nil)
        }
    }
}
