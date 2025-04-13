import { LocaleTreeItem, ProgressSubmenuItem } from '~/views';
import { CommandOptions } from '~/commands/manipulations/common';
export declare enum TelemetryKey {
    Activated = "activated",
    DeleteKey = "delete_key",
    Disabled = "disabled",
    EditKey = "edit_key",
    EditorOpen = "editor_open",
    Enabled = "enabled",
    ExtractString = "extract_string",
    ExtractStringBulk = "extract_string_bulk",
    GoToKey = "goto_key",
    InsertKey = "insert_key",
    Installed = "installed",
    NewKey = "new_key",
    RenameKey = "rename_key",
    ReviewAddComment = "review_add_comment",
    ReviewApplySuggestion = "review_apply_suggestion",
    ReviewApplyTranslation = "review_apply_translation",
    TranslateKey = "translate_key",
    Updated = "updated",
    ReviewEditComment = "review_edit_comment",
    ReviewResolveComment = "review_resolve_comment"
}
export declare enum ActionSource {
    None = "none",
    CommandPattele = "command_pattele",
    TreeView = "tree_view",
    Hover = "hover",
    ContextMenu = "context_menu",
    UiEditor = "ui_editor",
    Review = "review"
}
export declare class Telemetry {
    private static _userProperties;
    private static _amplitude;
    static track(key: TelemetryKey, properties?: Record<string, any>, immediate?: boolean): Promise<void>;
    static getActionSource(item?: LocaleTreeItem | ProgressSubmenuItem | CommandOptions): ActionSource;
    private static _initializeAmplitude;
    private static _getUserId;
    private static _getUserProperties;
}
