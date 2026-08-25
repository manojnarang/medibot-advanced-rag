export type Role = "doctor" | "nurse" | "billing_executive" | "technician" | "admin";

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in_minutes: number;
  role: Role;
  display_name: string;
  department: string;
  accessible_collections: string[];
}

export interface Session {
  token: string;
  username: string;
  role: Role;
  displayName: string;
  department: string;
  accessibleCollections: string[];
}

export interface Source {
  source_document: string;
  section_title: string;
  collection: string;
}

export type RetrievalType = "hybrid_rag" | "sql_rag" | "rbac_blocked";

export interface ChatResponse {
  answer: string;
  sources: Source[];
  retrieval_type: RetrievalType;
  role: Role;
}

export interface ChatMessage {
  id: string;
  role: "user" | "bot";
  text: string;
  sources?: Source[];
  retrievalType?: RetrievalType;
  pending?: boolean;
}

export interface CollectionInfo {
  name: string;
  label: string;
  description: string;
  documents: string[];
}

export interface CollectionsResponse {
  role: Role;
  accessible_collections: CollectionInfo[];
}
