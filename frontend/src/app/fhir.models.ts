export interface FhirResource {
  id?: string;
  resourceType: string;
}

export interface Patient extends FhirResource {
  resourceType: 'Patient';
  identifier?: { system: string, value: string }[];
  name?: { family: string, given: string[] }[];
  gender?: string;
  birthDate?: string;
}

export interface Observation extends FhirResource {
  resourceType: 'Observation';
  status: string;
  code: {
    coding: { system: string, code: string, display: string }[];
  };
  subject: { reference: string, display: string };
  effectiveDateTime: string;
  valueQuantity?: {
    value: number,
    unit: string,
    system: string,
    code: string
  };
}

export interface Practitioner extends FhirResource {
  resourceType: 'Practitioner';
  active: boolean;
  name?: { family: string, given: string[], prefix?: string[] }[];
  gender?: string;
  role?: string;
  specialty?: string;
  email?: string;
  phone?: string;
  qualification?: {
    code: {
      coding: { system: string, code: string, display: string }[],
      text: string
    }
  }[];
  telecom?: { system: string, value: string, use: string }[];
}

export interface Encounter extends FhirResource {
  resourceType: 'Encounter';
  status: string;
  class: { system: string, code: string, display: string };
  subject: { reference: string, display: string };
  period: { start: string, end?: string };
  reasonCode?: { text: string }[];
  participant?: {
    individual: { reference: string, display: string }
  }[];
}
