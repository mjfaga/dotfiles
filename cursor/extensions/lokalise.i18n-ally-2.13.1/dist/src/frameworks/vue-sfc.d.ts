import { Framework } from './base';
declare class VueSFCFramework extends Framework {
    id: string;
    display: string;
    detection: {
        packageJSON: string[];
    };
    languageIds: never[];
    usageMatchRegex: never[];
    refactorTemplates(): never[];
    enableFeatures: {
        VueSfc: boolean;
    };
}
export default VueSFCFramework;
