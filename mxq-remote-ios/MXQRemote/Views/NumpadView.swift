import SwiftUI
import ADBCore

struct NumpadView: View {
    @EnvironmentObject private var controller: RemoteController
    @EnvironmentObject private var settings: AppSettings

    private let rows: [[Int]] = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

    var body: some View {
        VStack(spacing: 18) {
            Spacer()
            ForEach(rows, id: \.self) { row in
                HStack(spacing: 18) {
                    ForEach(row, id: \.self) { digit in
                        digitButton(digit)
                    }
                }
            }
            HStack(spacing: 18) {
                actionButton(systemImage: "delete.left") {
                    controller.send(.del)
                }
                digitButton(0)
                actionButton(systemImage: "return", tint: Theme.accent) {
                    controller.send(.enter)
                }
            }
            Spacer()
        }
        .padding()
    }

    private func digitButton(_ digit: Int) -> some View {
        Button {
            controller.sendDigit(digit)
        } label: {
            Text("\(digit)")
                .font(.system(size: 30, weight: .semibold, design: .rounded))
                .foregroundColor(.white)
                .frame(width: 84, height: 84)
                .background(Circle().fill(Theme.surface))
        }
        .buttonStyle(PressedScaleStyle())
    }

    private func actionButton(systemImage: String, tint: Color = .white, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Image(systemName: systemImage)
                .font(.system(size: 26, weight: .semibold))
                .foregroundColor(tint)
                .frame(width: 84, height: 84)
                .background(Circle().fill(Theme.surface))
        }
        .buttonStyle(PressedScaleStyle())
    }
}
