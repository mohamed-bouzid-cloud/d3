# Healthcare FHIR Platform: Project Architecture & Technical Report

---

## 1. Executive Summary

This document serves as a comprehensive technical and architectural report for the Healthcare FHIR Platform (internally designated as the "d3" project). The platform is a modern, full-stack Electronic Health Record (EHR) system designed to adhere to a subset of the **HL7 FHIR (Fast Healthcare Interoperability Resources) R4** standard. 

The system facilitates the management of patients, healthcare practitioners, clinical observations, and medical encounters through a decoupled architecture featuring a robust Python/Django backend and a responsive Angular frontend.

---

## 2. Technology Stack

The project utilizes a modern, enterprise-grade technology stack ensuring high performance, scalability, and maintainability:

### Backend 
*   **Framework:** Django & Django REST Framework (DRF)
*   **API Specification:** OpenAPI 3.0 via `drf-spectacular` (Swagger UI integrated)
*   **Authentication:** JSON Web Tokens (JWT) via `rest_framework_simplejwt`
*   **Filtering:** `django-filter` for advanced query capabilities
*   **Database:** SQLite (development configuration, production-ready for migration to PostgreSQL)

### Frontend
*   **Framework:** Angular (v21.2.x)
*   **Language:** TypeScript 5.9.x
*   **Styling:** SCSS
*   **State & HTTP Management:** RxJS, Angular `HttpClient`
*   **Testing:** Vitest & JSDom

---

## 3. System Architecture

The application follows a standard decoupled Client-Server architecture:

```mermaid
graph LR
    A[Angular Client] <-->|JSON / REST (JWT Auth)| B(Django REST API)
    B <--> C[(SQLite Database)]
```

### Security & Authentication
Authentication is strictly enforced using **JWT (JSON Web Tokens)**. 
- The Angular client authenticates via `/api/token/` and stores the resulting access and refresh tokens.
- All subsequent requests to protected FHIR endpoints are verified using the `Authorization: Bearer <token>` header, seamlessly handled by the Angular `AuthService` and `FhirService`.

---

## 4. Core Domain Model (FHIR Resources)

The backend implements four primary entities mirroring the FHIR R4 standard. Each entity is uniquely identified using UUIDs and indexed for performance.

### 4.1 Patient
Represents a patient receiving care.
*   **Fields:** Identifier (UUID), Family Name, Given Name, Birth Date, Gender.
*   **Indexes:** Optimized for search by UUID and name.

### 4.2 Practitioner
Represents a healthcare provider (Doctor, Nurse, Specialist, etc.).
*   **Fields:** Identifier (UUID), Name, Gender, Role, RPPS Number (French healthcare ID), Specialty, Contact Information.

### 4.3 Observation
Represents a clinical measurement or finding (e.g., Blood Pressure, Heart Rate).
*   **Fields:** Patient (Foreign Key), Observation Type, Value, Unit, Effective Date.

### 4.4 Encounter
Represents an interaction between a Patient and a Practitioner.
*   **Fields:** Patient, Practitioner, Status (Planned, In-progress, Finished), Class (Ambulatory, Inpatient, Emergency), Reason, Start Date, End Date.

---

## 5. API Specification & Endpoints

The API is fully documented via an auto-generated Swagger UI accessible at `/api/docs/`. Key endpoints include:

| Resource | Endpoint | Supported Methods | Description |
| :--- | :--- | :--- | :--- |
| **Authentication** | `/api/token/` | `POST` | Obtain JWT access/refresh pairs |
| **Patients** | `/api/patients/` | `GET`, `POST`, `PUT`, `DELETE` | Full CRUD operations for Patients |
| **Observations** | `/api/patients/{id}/observations/` | `GET` | Nested route for a patient's observations |
| **Practitioners** | `/api/practitioners/` | `GET`, `POST`, `PUT`, `DELETE` | Full CRUD operations for Practitioners |
| **Encounters** | `/api/practitioners/{id}/encounters/`| `GET` | Nested route for practitioner encounters |

*Note: All endpoints support advanced filtering (e.g., filtering encounters by status, date ranges, or specific practitioners).*

---

## 6. Frontend Application Structure

The Angular frontend is structured to provide a scalable foundation for clinical UI components.

*   **`fhir.service.ts`:** A generic, highly-reusable HTTP wrapper for FHIR resources. It utilizes TypeScript generics (`<T>`) to provide type-safe CRUD operations (`getResources`, `getResourceById`, `createResource`) and handles JWT token injection.
*   **`auth.service.ts`:** Manages user session state, JWT lifecycle, and authorization headers.
*   **`fhir.models.ts`:** Contains TypeScript interfaces mirroring the backend Django models, ensuring strict typing across the network boundary.

---

## 7. Strategic Recommendations & Next Steps

To elevate the project to production readiness, the following enhancements are recommended:

1.  **Database Migration:** Transition from SQLite to PostgreSQL for concurrent transaction handling.
2.  **Environment Variables:** Abstract secrets, debug flags, and database credentials into `.env` files.
3.  **FHIR Validation:** Implement strict JSON Schema validation to ensure payloads strictly match the official HL7 FHIR R4 specifications beyond basic Django model validation.
4.  **UI/UX Polish:** Leverage Angular Animations (already installed) and SCSS to build out premium, glassmorphism-inspired clinical dashboards for data visualization.

---
*Report automatically generated for project stakeholder review.*
