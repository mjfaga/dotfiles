import { ProgressSubmenuItem } from './ProgressSubmenuItem';
import { ProgressRootItem } from './ProgressRootItem';
export declare class ProgressTranslatedListItem extends ProgressSubmenuItem {
    protected root: ProgressRootItem;
    constructor(root: ProgressRootItem);
    getKeys(): string[];
}
