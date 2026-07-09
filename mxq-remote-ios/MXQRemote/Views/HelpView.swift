import SwiftUI

struct HelpView: View {
    @EnvironmentObject private var settings: AppSettings

    private let stepKeys = ["help_step_1", "help_step_2", "help_step_3", "help_step_4", "help_step_5", "help_step_6"]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                Text(settings.tr("help_intro"))
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                VStack(alignment: .leading, spacing: 14) {
                    ForEach(Array(stepKeys.enumerated()), id: \.offset) { index, key in
                        HStack(alignment: .top, spacing: 12) {
                            Text("\(index + 1)")
                                .font(.subheadline.weight(.bold))
                                .foregroundColor(.black)
                                .frame(width: 26, height: 26)
                                .background(Circle().fill(Theme.accent))
                            Text(settings.tr(key))
                                .font(.subheadline)
                        }
                    }
                }
                .padding(16)
                .background(RoundedRectangle(cornerRadius: 16).fill(Theme.surface))

                sectionCard(titleKey: "help_first_title", bodyKey: "help_first_body", icon: "checkmark.shield")
                sectionCard(titleKey: "help_trouble_title", bodyKey: "help_trouble_body", icon: "wrench.and.screwdriver")

                Text(settings.tr("err_local_network"))
                    .font(.footnote)
                    .foregroundColor(.secondary)
            }
            .padding(20)
        }
        .background(Theme.background)
        .navigationTitle(settings.tr("help_title"))
        .navigationBarTitleDisplayMode(.inline)
    }

    private func sectionCard(titleKey: String, bodyKey: String, icon: String) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Label(settings.tr(titleKey), systemImage: icon)
                .font(.headline)
            Text(settings.tr(bodyKey))
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(RoundedRectangle(cornerRadius: 16).fill(Theme.surface))
    }
}
