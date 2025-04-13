import { ExtensionModule } from '~/modules';
export declare class ConfigLocalesGuide {
    static prompt(): Promise<void>;
    static config(): Promise<void>;
    static pickDir(): Promise<string[]>;
    static success(): Promise<void>;
    static autoSet(): Promise<void>;
}
declare const _default: ExtensionModule;
export default _default;
