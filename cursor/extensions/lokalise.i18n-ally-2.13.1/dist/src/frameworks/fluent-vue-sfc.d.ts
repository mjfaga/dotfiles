import { Framework } from './base';
declare class FluentVueSFCFramework extends Framework {
    id: string;
    display: string;
    detection: {
        packageJSON: string[];
    };
    languageIds: never[];
    usageMatchRegex: never[];
    refactorTemplates(): never[];
    enableFeatures: {
        FluentVueSfc: boolean;
    };
}
export default FluentVueSFCFramework;
