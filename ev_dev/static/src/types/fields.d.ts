declare module "@web/views/fields/standard_field_props" {
  import type { Record } from "@web/model/relational_model/record";
  export type StandardFieldProps = {
    id?: string;
    name: string;
    readonly?: boolean;
    record: Record;
  }

  export const standardFieldProps: StandardFieldProps = {}
}
