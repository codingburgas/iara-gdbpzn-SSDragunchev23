from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import time

from sqlalchemy import create_engine, Column, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://iara_user:iara_pass@db:5432/iara_db")

time.sleep(2)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBVessel(Base):
    __tablename__ = "vessels"
    
    vessel_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    flag = Column(String, default="BG")
    home_port = Column(String, nullable=False)
    length_overall = Column(Float, nullable=False)
    active_license = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_initial_data():
    db = SessionLocal()
    if db.query(DBVessel).count() == 0:
        initial_vessels = [
            DBVessel(vessel_id="BGR0012304", name="Black Sea Pearl", flag="BG", home_port="Burgas", length_overall=14.5, active_license=True),
            DBVessel(vessel_id="BGR0056709", name="Saint Nicholas", flag="BG", home_port="Varna", length_overall=22.1, active_license=True),
            DBVessel(vessel_id="BGR0022441", name="Poseidon", flag="BG", home_port="Sozopol", length_overall=9.8, active_license=False),
            DBVessel(vessel_id="BGR0044112", name="Kaliakra", flag="BG", home_port="Balchik", length_overall=18.2, active_license=True),
            DBVessel(vessel_id="BGR0077334", name="Aegean Breeze", flag="BG", home_port="Nesebar", length_overall=12.4, active_license=True),
            DBVessel(vessel_id="BGR0099556", name="Captain Jack", flag="BG", home_port="Burgas", length_overall=26.5, active_license=True),
            DBVessel(vessel_id="BGR0033667", name="Sea Wolf", flag="BG", home_port="Varna", length_overall=15.1, active_license=False),
            DBVessel(vessel_id="BGR0088221", name="Amphitrite", flag="BG", home_port="Sozopol", length_overall=11.3, active_license=True)
        ]
        db.add_all(initial_vessels)
        db.commit()
    db.close()

seed_initial_data()

class VesselSchema(BaseModel):
    vessel_id: str = Field(..., description="Unique CFR number of the vessel", example="BGR0012304")
    name: str = Field(..., description="Name of the vessel", example="Black Sea Pearl")
    flag: str = Field("BG", description="Country flag")
    home_port: str = Field(..., description="Home port of registration", example="Burgas")
    length_overall: float = Field(..., description="Length overall in meters", example=14.5)
    active_license: bool = Field(True, description="Licensing status")

    class Config:
        from_attributes = True

class LicenseUpdateSchema(BaseModel):
    active_license: bool

app = FastAPI(
    title="IARA · Fleet Management Backend",
    description="Professional backend system connected to a live PostgreSQL database via Docker Compose.",
    version="2.2.0"
)

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
def read_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IARA Fleet Control Tower</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-900 text-slate-100 min-h-screen font-sans">
        <!-- Navigation -->
        <nav class="bg-slate-800 border-b border-slate-700 p-4 shadow-lg">
            <div class="max-w-6xl mx-auto flex justify-between items-center">
                <div class="flex items-center space-x-3">
                    <span class="text-2xl">⚓</span>
                    <h1 class="text-xl font-bold tracking-wider text-teal-400">IARA · Fleet Control (Live DB)</h1>
                </div>
                <div class="flex space-x-4 text-sm text-slate-400">
                    <a href="/docs" class="hover:text-teal-400 transition font-medium">Swagger API Docs</a>
                </div>
            </div>
        </nav>

        <main class="max-w-6xl mx-auto p-6 mt-6">
            
            <!-- LIVE STATISTICS CARDS -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="bg-slate-800 p-5 rounded-xl border border-slate-700 shadow-md flex items-center justify-between">
                    <div>
                        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Vessels</p>
                        <h3 id="statTotal" class="text-3xl font-black text-white mt-1">0</h3>
                    </div>
                    <span class="text-3xl p-3 bg-slate-700/50 rounded-lg">🚢</span>
                </div>
                <div class="bg-slate-800 p-5 rounded-xl border border-slate-700 shadow-md flex items-center justify-between">
                    <div>
                        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Active Licenses</p>
                        <h3 id="statActive" class="text-3xl font-black text-emerald-400 mt-1">0</h3>
                    </div>
                    <span class="text-3xl p-3 bg-emerald-500/10 rounded-lg">✅</span>
                </div>
                <div class="bg-slate-800 p-5 rounded-xl border border-slate-700 shadow-md flex items-center justify-between">
                    <div>
                        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Avg Length</p>
                        <h3 id="statAvgLength" class="text-3xl font-black text-teal-400 mt-1">0 m</h3>
                    </div>
                    <span class="text-3xl p-3 bg-teal-500/10 rounded-lg">📐</span>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <!-- VESSEL REGISTRATION FORM -->
                <div class="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl h-fit">
                    <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
                        <span>➕</span> Register New Vessel
                    </h3>
                    <form id="addVesselForm" onsubmit="submitVessel(event)" class="space-y-4">
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">CFR Number (Unique)</label>
                            <input type="text" id="vessel_id" required placeholder="e.g. BGR0012345" class="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-teal-500">
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-slate-400 mb-1">Vessel Name</label>
                            <input type="text" id="name" required placeholder="e.g. Black Sea Pearl" class="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-teal-500">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Home Port</label>
                                <select id="home_port" required class="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-teal-500">
                                    <option value="Burgas">Burgas</option>
                                    <option value="Varna">Varna</option>
                                    <option value="Sozopol">Sozopol</option>
                                    <option value="Nesebar">Nesebar</option>
                                    <option value="Balchik">Balchik</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-400 mb-1">Length (meters)</label>
                                <input type="number" step="0.1" id="length_overall" required placeholder="14.5" class="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-teal-500">
                            </div>
                        </div>
                        <button type="submit" class="w-full bg-teal-500 hover:bg-teal-600 text-slate-900 font-bold py-2.5 rounded-lg text-sm transition shadow-md">
                            Register Vessel
                        </button>
                    </form>
                </div>

                <!-- VESSEL LIST TABLE -->
                <div class="lg:col-span-2 space-y-4">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center p-4 bg-slate-800 rounded-xl border border-slate-700 gap-4">
                        <h4 class="font-bold text-white text-md">Active Fleet Registry</h4>
                        <select id="portFilter" onchange="loadVessels()" class="bg-slate-700 border border-slate-600 text-white text-xs rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 w-44">
                            <option value="">All Ports</option>
                            <option value="Burgas">Burgas</option>
                            <option value="Varna">Varna</option>
                            <option value="Sozopol">Sozopol</option>
                            <option value="Nesebar">Nesebar</option>
                            <option value="Balchik">Balchik</option>
                        </select>
                    </div>

                    <div class="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
                        <table class="w-full text-left border-collapse">
                            <thead>
                                <tr class="bg-slate-750 border-b border-slate-700 text-slate-400 text-xs font-semibold uppercase tracking-wider">
                                    <th class="p-4">CFR Number</th>
                                    <th class="p-4">Name</th>
                                    <th class="p-4">Port</th>
                                    <th class="p-4">Length</th>
                                    <th class="p-4">License</th>
                                </tr>
                            </thead>
                            <tbody id="vesselsTableBody" class="divide-y divide-slate-700 text-sm text-slate-300">
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>

        <script>
            async function loadVessels() {
                const port = document.getElementById('portFilter').value;
                let url = '/api/v1/vessels';
                if (port) { url += `?port=${port}`; }

                try {
                    const response = await fetch(url);
                    const vessels = await response.json();
                    const tableBody = document.getElementById('vesselsTableBody');
                    tableBody.innerHTML = '';

                    vessels.forEach(vessel => {
                        const licenseBadge = vessel.active_license 
                            ? `<span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-0.5 rounded-full text-xs font-medium">Active</span>`
                            : `<span class="bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2.5 py-0.5 rounded-full text-xs font-medium">Expired</span>`;

                        tableBody.innerHTML += `
                            <tr class="hover:bg-slate-750/50 transition">
                                <td class="p-4 font-mono text-teal-400 font-medium">${vessel.vessel_id}</td>
                                <td class="p-4 font-semibold text-white">${vessel.name}</td>
                                <td class="p-4">${vessel.home_port}</td>
                                <td class="p-4">${vessel.length_overall} m</td>
                                <td class="p-4">${licenseBadge}</td>
                            </tr>
                        `;
                    });

                    const allRes = await fetch('/api/v1/vessels');
                    const allVessels = await allRes.json();
                    
                    const total = allVessels.length;
                    const active = allVessels.filter(v => v.active_license).length;
                    const avgLen = total > 0 ? (allVessels.reduce((acc, v) => acc + v.length_overall, 0) / total).toFixed(1) : 0;

                    document.getElementById('statTotal').innerText = total;
                    document.getElementById('statActive').innerText = active;
                    document.getElementById('statAvgLength').innerText = `${avgLen} m`;

                } catch (error) {
                    console.error('Error:', error);
                }
            }

            async function submitVessel(event) {
                event.preventDefault();
                
                const payload = {
                    vessel_id: document.getElementById('vessel_id').value,
                    name: document.getElementById('name').value,
                    flag: "BG",
                    home_port: document.getElementById('home_port').value,
                    length_overall: parseFloat(document.getElementById('length_overall').value),
                    active_license: true
                };

                try {
                    const response = await fetch('/api/v1/vessels', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });

                    if (response.ok) {
                        document.getElementById('addVesselForm').reset();
                        loadVessels();
                    } else {
                        const errData = await response.json();
                        alert(`Error: ${errData.detail}`);
                    }
                } catch (error) {
                    alert('Connection issue with the backend.');
                }
            }

            window.onload = loadVessels;
        </script>
    </body>
    </html>
    """
    return html_content



@app.get("/api/v1/vessels", response_model=List[VesselSchema], tags=["Vessels"])
def get_vessels(port: Optional[str] = None, db: Session = Depends(get_db)):
    """Fetch all vessels from PostgreSQL with optional port filtering"""
    query = db.query(DBVessel)
    if port:
        query = query.filter(DBVessel.home_port.ilike(port))
    return query.all()

@app.get("/api/v1/vessels/{vessel_id}", response_model=VesselSchema, tags=["Vessels"])
def get_vessel(vessel_id: str, db: Session = Depends(get_db)):
    """Get details of a single vessel by its CFR ID"""
    vessel = db.query(DBVessel).filter(DBVessel.vessel_id.ilike(vessel_id)).first()
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel with CFR {vessel_id} not found.")
    return vessel

@app.post("/api/v1/vessels", status_code=status.HTTP_201_CREATED, response_model=VesselSchema, tags=["Vessels"])
def create_vessel(vessel: VesselSchema, db: Session = Depends(get_db)):
    """Register a brand new vessel in the live database"""
    existing = db.query(DBVessel).filter(DBVessel.vessel_id.ilike(vessel.vessel_id)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vessel with this CFR already exists.")
    
    db_vessel = DBVessel(**vessel.model_dump())
    db.add(db_vessel)
    db.commit()
    db.refresh(db_vessel)
    return db_vessel

@app.put("/api/v1/vessels/{vessel_id}/license", response_model=VesselSchema, tags=["Licensing"])
def update_license(vessel_id: str, update_data: LicenseUpdateSchema, db: Session = Depends(get_db)):
    """Update commercial fishing license status (Active/Expired)"""
    vessel = db.query(DBVessel).filter(DBVessel.vessel_id.ilike(vessel_id)).first()
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel with CFR {vessel_id} not found.")
    
    vessel.active_license = update_data.active_license
    db.commit()
    db.refresh(vessel)
    return vessel

@app.delete("/api/v1/vessels/{vessel_id}", tags=["Vessels"])
def delete_vessel(vessel_id: str, db: Session = Depends(get_db)):
    """Decommission and remove a vessel permanently from the live registry"""
    vessel = db.query(DBVessel).filter(DBVessel.vessel_id.ilike(vessel_id)).first()
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel with CFR {vessel_id} not found.")
    
    db.delete(vessel)
    db.commit()
    return {"message": f"Vessel {vessel_id} successfully decommissioned from the live database."}