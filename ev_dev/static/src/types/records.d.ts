declare module "@web/model/relational_model/record" {
  export type Mode = "edit" | "readonly";

  export interface Many2OneValue {
    id: number;
    display_name: string;
  }

  export interface RecordConfig {
    resId?: number;
    resIds?: number[];
    mode?: Mode;
    isRoot?: boolean;
  }

  export interface RecordData {
    [key: string]: any;
  }

  export interface Record {
    // 🔹 básicos
    readonly resId?: number;
    readonly resIds?: number[];
    readonly data: RecordData;
    readonly dirty: boolean;
    readonly selected: boolean;

    // 🔹 estado
    readonly isNew: boolean;
    readonly isValid: boolean;
    readonly isInEdition: boolean;
    readonly isActive: boolean;

    // 🔹 config
    readonly config: RecordConfig;

    // 🔹 acciones principales
    save(options?: any): Promise<boolean>;
    load(): Promise<void>;
    delete(): Promise<boolean>;
    duplicate(): Promise<void>;
    discard(): Promise<void>;

    // 🔹 cambios
    update(changes: RecordData, options?: { save?: boolean }): Promise<void>;
    getChanges(options?: { withReadonly?: boolean }): Promise<RecordData>;
    isDirty(): Promise<boolean>;

    // 🔹 validación
    checkValidity(options?: {
      displayNotification?: boolean;
    }): Promise<boolean>;
    isFieldInvalid(fieldName: string): boolean;
    setInvalidField(fieldName: string): Promise<void>;
    resetFieldValidity(fieldName: string): Promise<void>;

    // 🔹 modo
    switchMode(mode: Mode): void;

    // 🔹 util
    archive(): Promise<void>;
    unarchive(): Promise<void>;
    toggleSelection(selected?: boolean): void;

    // 🔹 contexto importante
    evalContext: Record<string, any>;
  }
}
