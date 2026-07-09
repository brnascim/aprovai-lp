import SwiftUI
import ADBCore

struct TextInputView: View {
    @EnvironmentObject private var controller: RemoteController
    @EnvironmentObject private var settings: AppSettings

    @State private var text = ""
    @State private var pressEnterAfterSend = true
    @FocusState private var fieldFocused: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            Text(settings.tr("text_title"))
                .font(.headline)

            TextField(settings.tr("text_placeholder"), text: $text, axis: .vertical)
                .lineLimit(3, reservesSpace: true)
                .textFieldStyle(.plain)
                .padding(12)
                .background(RoundedRectangle(cornerRadius: 14).fill(Theme.surface))
                .focused($fieldFocused)
                .submitLabel(.send)
                .onSubmit(send)

            Toggle(settings.tr("text_send_enter"), isOn: $pressEnterAfterSend)
                .tint(Theme.accent)

            Button(action: send) {
                Label(settings.tr("text_send"), systemImage: "paperplane.fill")
                    .frame(maxWidth: .infinity)
                    .fontWeight(.semibold)
            }
            .buttonStyle(.borderedProminent)
            .tint(Theme.accent)
            .disabled(text.isEmpty)

            HStack(spacing: 16) {
                RoundRemoteButton(systemImage: "delete.left", size: 50) { controller.send(.del) }
                RoundRemoteButton(systemImage: "return", size: 50) { controller.send(.enter) }
                Spacer()
            }

            Text(settings.tr("text_hint"))
                .font(.footnote)
                .foregroundColor(.secondary)

            Spacer()
        }
        .padding(20)
        .onAppear { fieldFocused = true }
    }

    private func send() {
        controller.sendText(text, pressEnter: pressEnterAfterSend)
        text = ""
    }
}
