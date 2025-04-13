import { ProgressRootItem } from './ProgressRootItem';
import { ProgressSubmenuItem } from './ProgressSubmenuItem';
export declare class ProgressEmptyListItem extends ProgressSubmenuItem {
    protected root: ProgressRootItem;
    constructor(root: ProgressRootItem);
    get contextValue(): string;
    getKeys(): string[];
}
