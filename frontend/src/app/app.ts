import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from './auth.service';
import { FhirService } from './fhir.service';
import { Patient, Observation, Practitioner, Encounter } from './fhir.models';

type ResourceType = 'patients' | 'observations' | 'practitioners' | 'encounters';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  // UI State
  activeTab = signal<ResourceType>('patients');
  loading = signal(false);
  showForm = signal(false);
  editingId = signal<string | null>(null);

  // Data
  resources = signal<any[]>([]);
  searchQuery = signal('');
  filteredResources = computed(() => {
    const q = this.searchQuery().toLowerCase().trim();
    if (!q) return this.resources();
    return this.resources().filter(res => {
      const searchStr = JSON.stringify(res).toLowerCase();
      return searchStr.includes(q);
    });
  });

  // Selection Lists (for linking resources)
  patientList = signal<Patient[]>([]);
  practitionerList = signal<Practitioner[]>([]);

  // Stats
  totalPatients = signal(0);
  totalObservations = signal(0);
  activeEncounters = signal(0);
  activePractitioners = signal(0);

  // Form Model
  formModel: any = {};

  constructor(public auth: AuthService, private fhir: FhirService) {}

  ngOnInit() {
    this.refreshAll();
  }

  refreshAll() {
    this.loadResources();
    this.preloadSelections();
    this.calculateStats();
  }

  calculateStats() {
    this.fhir.getResources<any>('patients').subscribe(data => {
      const list = (data as any).results || data;
      this.totalPatients.set((data as any).count ?? list.length);
    });
    this.fhir.getResources<any>('observations').subscribe(data => {
      const list = (data as any).results || data;
      this.totalObservations.set((data as any).count ?? list.length);
    });
    this.fhir.getResources<any>('encounters').subscribe(data => {
      const list = (data as any).results || data;
      this.activeEncounters.set((data as any).count ?? list.length);
    });
    this.fhir.getResources<any>('practitioners').subscribe(data => {
      const list = (data as any).results || data;
      this.activePractitioners.set((data as any).count ?? list.length);
    });
  }

  preloadSelections() {
    this.fhir.getResources<any>('patients').subscribe(data => {
      const list = (data as any).results || data;
      this.patientList.set(list);
    });
    this.fhir.getResources<any>('practitioners').subscribe(data => {
      const list = (data as any).results || data;
      this.practitionerList.set(list);
    });
  }

  logout() {
    this.auth.logout();
    this.resources.set([]);
  }

  setTab(tab: ResourceType) {
    this.activeTab.set(tab);
    this.showForm.set(false);
    this.loadResources();
  }

  loadResources() {
    this.loading.set(true);
    this.fhir.getResources<any>(this.activeTab()).subscribe({
      next: (data) => {
        // Handle DRF pagination results
        const unwrapped = (data as any).results || data;
        this.resources.set(unwrapped);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  openCreateForm() {
    this.editingId.set(null);
    this.formModel = this.getDefaultModel(this.activeTab()) || {};
    this.showForm.set(true);
  }

  openEditForm(resource: any) {
    this.editingId.set(resource.id || resource.identifier);
    // Transform FHIR format back to form-friendly format if needed
    this.formModel = this.flattenForForm(resource);
    this.showForm.set(true);
  }

  save() {
    const type = this.activeTab();
    const id = this.editingId();
    const payload = this.preparePayload(this.formModel, type);

    const obs = id 
      ? this.fhir.updateResource(type, id, payload)
      : this.fhir.createResource(type, payload);

    obs.subscribe({
      next: () => {
        this.showForm.set(false);
        this.refreshAll();
      },
      error: (err) => {
        console.error('Save failed:', err);
      }
    });
  }

  delete(id: string) {
    if (confirm('Are you sure you want to delete this resource?')) {
      this.fhir.deleteResource(this.activeTab(), id).subscribe(() => {
        this.refreshAll();
      });
    }
  }

  private getDefaultModel(type: ResourceType) {
    switch (type) {
      case 'patients': return { 
        resourceType: 'Patient', 
        name: [{ family: '', given: [''] }], 
        gender: 'unknown', 
        birthDate: new Date().toISOString().split('T')[0] 
      };
      case 'observations': return { 
        resourceType: 'Observation', 
        status: 'final', 
        code: { coding: [{ display: '', code: '' }] }, 
        subject: { reference: '' }, 
        valueQuantity: { value: null, unit: '' } 
      };
      case 'practitioners': return { 
        resourceType: 'Practitioner', 
        active: true, 
        name: [{ family: '', given: [''] }], 
        role: 'doctor',
        specialty: '',
        phone: '',
        email: '' 
      };
      case 'encounters': return { 
        resourceType: 'Encounter', 
        status: 'planned', 
        class: { code: '', display: '' }, 
        subject: { reference: '' },
        participant: [{ individual: { reference: '' } }],
        period: { start: new Date().toISOString() },
        reasonCode: [{ text: '' }]
      };
    }
  }

  private flattenForForm(res: any) {
    return JSON.parse(JSON.stringify(res));
  }

  private preparePayload(model: any, type: ResourceType) {
    // Ensuring backend-compatible FHIR structure
    // The backend serializers often expect specific structures
    const payload = JSON.parse(JSON.stringify(model));
    
    // Ensure "id" is removed for "Create"
    if (!this.editingId()) {
      delete payload.id;
      delete payload.identifier;
    }

    return payload;
  }

  // UI Helpers
  getDisplayName(res: any): string {
    if (res.name) {
      const name = res.name[0];
      return `${name.family || ''} ${name.given ? name.given[0] : ''}`;
    }
    if (res.code?.coding) return res.code.coding[0].display;
    if (res.resourceType === 'Encounter') return `Encounter: ${res.reasonCode?.[0]?.text || res.status}`;
    return res.id || res.identifier || 'Unnamed';
  }
}
