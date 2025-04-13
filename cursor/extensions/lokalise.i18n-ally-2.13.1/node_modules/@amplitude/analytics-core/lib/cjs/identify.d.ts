import { IdentifyUserProperties, ValidPropertyType, Identify as IIdentify } from '@amplitude/analytics-types';
export declare class Identify implements IIdentify {
    protected readonly _propertySet: Set<string>;
    protected _properties: IdentifyUserProperties;
    getUserProperties(): IdentifyUserProperties;
    set(property: string, value: ValidPropertyType): Identify;
    setOnce(property: string, value: ValidPropertyType): Identify;
    append(property: string, value: ValidPropertyType): Identify;
    prepend(property: string, value: ValidPropertyType): Identify;
    postInsert(property: string, value: ValidPropertyType): Identify;
    preInsert(property: string, value: ValidPropertyType): Identify;
    remove(property: string, value: ValidPropertyType): Identify;
    add(property: string, value: number): Identify;
    unset(property: string): Identify;
    clearAll(): Identify;
    private _safeSet;
    private _validate;
}
//# sourceMappingURL=identify.d.ts.map