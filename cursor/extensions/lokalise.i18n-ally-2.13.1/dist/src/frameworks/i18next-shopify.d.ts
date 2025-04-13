import ReactI18nextFramework from './react-i18next';
import { DirStructure, KeyStyle } from '~/core';
declare class ShopifyI18nextFramework extends ReactI18nextFramework {
    id: string;
    display: string;
    preferredKeystyle?: KeyStyle;
    preferredDirStructure?: DirStructure;
    detection: {
        packageJSON: string[];
    };
    derivedKeyRules: string[];
}
export default ShopifyI18nextFramework;
