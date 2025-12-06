import React, { useState } from 'react';
import { Building2, Search, FileText, Award, TrendingUp, AlertCircle, Loader, Globe, CheckCircle, ChevronDown } from 'lucide-react';

const DellDashboard = () => {
  const [task, setTask] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Task 1
  const [selectedCategory, setSelectedCategory] = useState('');
  const [market, setMarket] = useState(null);
  
  // Task 2
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [contract, setContract] = useState(null);
  
  // Task 3
  const [score1, setScore1] = useState(null);
  const [score2, setScore2] = useState(null);

  const categories = [
    'Electronics & Semiconductors',
    'Packaging Materials',
    'Logistics & Transportation',
    'Chemicals & Materials',
    'IT Services & Software',
    'Hardware Components',
    'Cloud Computing Services',
    'Network Equipment',
    'Data Storage Solutions',
    'Manufacturing Equipment',
    'Office Supplies',
    'Energy & Utilities'
  ];

  const dellProducts = [
    'Laptop Components (Displays, Batteries, Keyboards)',
    'Server Components (Processors, Memory, Storage)',
    'Semiconductor & Microchips',
    'Printed Circuit Boards (PCBs)',
    'Cooling Systems & Thermal Solutions',
    'Power Supply Units',
    'Networking Equipment (Switches, Routers)',
    'Data Storage Devices (SSDs, HDDs)',
    'Graphics Processing Units (GPUs)',
    'Packaging Materials',
    'Logistics & Freight Services',
    'Software Licensing',
    'Cloud Infrastructure Services',
    'IT Support & Consulting',
    'Security & Compliance Solutions',
    'Manufacturing Equipment & Tools',
    'Testing & Quality Assurance Equipment',
    'Raw Materials (Plastics, Metals, Composites)'
  ];

  const call = async (p) => {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model: "claude-sonnet-4-20250514", max_tokens: 4000, messages: [{ role: "user", content: p }] })
    });
    const d = await r.json();
    return d.content.map(i => i.type === "text" ? i.text : "").join("\n");
  };

  const doMarket = async () => {
    if (!selectedCategory) { setError('Please select a category'); return; }
    setLoading(true); setError('');
    try {
      const p = `For Dell Technologies, analyze supplier market for: "${selectedCategory}". Return JSON: {category:"${selectedCategory}",marketOverview:"2-3 sentence overview",topSuppliers:[{rank:1-5,name:"Company",headquarters:"City, Country",marketShare:"X%",annualRevenue:"$X billion",keyCapabilities:["cap1","cap2","cap3","cap4"],differentiators:"unique advantages",dellRelevance:"why relevant to Dell"}],countryRisks:[{country:"Country",supplierConcentration:"High/Medium/Low",politicalRisk:{score:"1-10",assessment:"detailed",keyFactors:["factor1","factor2"]},logisticsRisk:{score:"1-10",assessment:"detailed",keyFactors:["factor1","factor2"]},complianceRisk:{score:"1-10",assessment:"detailed",keyFactors:["factor1","factor2"]},esgRisk:{score:"1-10",assessment:"detailed",keyFactors:["factor1","factor2"]},overallRiskLevel:"High/Medium/Low",mitigation:"strategies"}]}. Provide exactly 5 suppliers and 3-4 sourcing countries. Return ONLY valid JSON, no markdown.`;
      const res = await call(p);
      setMarket(JSON.parse(res.replace(/```json|```/g, "").trim()));
    } catch (e) { setError(e.message); } finally { setLoading(false); }
  };

  const doContract = async () => {
    if (selectedProducts.length === 0) { setError('Please select at least one product/service'); return; }
    setLoading(true); setError('');
    try {
      const productList = selectedProducts.join(', ');
      const p = `For Dell Technologies, analyze contract types (FFP/T&M/CR) for these products/services: ${productList}. For EACH product, evaluate: Cost Predictability (High/Medium/Low + reason), Market Volatility (High/Medium/Low + reason), Duration (Short/Medium/Long-term + reason), Volume (Fixed/Variable + reason). Return JSON: {analysisDate:"2025-12-06",categories:[{name:"product name",assessment:{costPredictability:"High/Medium/Low",costPredictabilityReason:"why",marketVolatility:"High/Medium/Low",marketVolatilityReason:"why",duration:"Short/Medium/Long-term",durationReason:"why",volume:"Fixed/Variable",volumeReason:"why"},recommendedContract:"FFP/T&M/CR",confidence:"High/Medium",justification:"3-4 sentences explaining why this contract type",alternativeOption:"alternative if conditions change",riskConsiderations:["risk1","risk2","risk3"],keyContractClauses:["clause1","clause2"]}],contractComparison:{FFP:{suitability:"when to use",advantages:["adv1","adv2","adv3"],disadvantages:["dis1","dis2"],dellExamples:["ex1","ex2"]},TM:{suitability:"when to use",advantages:["adv1","adv2","adv3"],disadvantages:["dis1","dis2"],dellExamples:["ex1","ex2"]},CR:{suitability:"when to use",advantages:["adv1","adv2","adv3"],disadvantages:["dis1","dis2"],dellExamples:["ex1","ex2"]}},procurementRecommendations:["rec1","rec2","rec3"]}. Return ONLY valid JSON, no markdown.`;
      const res = await call(p);
      setContract(JSON.parse(res.replace(/```json|```/g, "").trim()));
    } catch (e) { setError(e.message); } finally { setLoading(false); }
  };

  const doScorecard = async () => {
    setLoading(true); setError('');
    try {
      const p1 = `Create comprehensive supplier evaluation scorecard for Dell Technologies IT Services industry. Must include exactly 5 dimensions: Technical Capability (25%), Quality Performance (20%), Financial Health (20%), ESG Compliance (20%), Innovation Capability (15%). Return JSON: {organization:"Dell Technologies",category:"General Procurement",industry:"IT Services",generatedDate:"2025-12-06",totalMaxScore:100,dimensions:[{name:"dimension name",weight:number,description:"what it assesses",kpis:[{name:"KPI name",description:"what it measures",measurement:"how to measure with specific metrics",target:"target value or benchmark",maxScore:number,scoringCriteria:{excellent:"9-10 points: criteria",good:"7-8 points: criteria",acceptable:"5-6 points: criteria",poor:"0-4 points: criteria"}}]}],overallScoringGuide:{excellent:"90-100 points: World-class supplier",good:"75-89 points: Strong supplier",acceptable:"60-74 points: Acceptable with monitoring",poor:"Below 60: Not recommended"},evaluationProcess:["step1","step2","step3"],recommendations:["rec1","rec2","rec3"]}. Each dimension should have 3-4 specific KPIs. Weights must sum to 100%. Return ONLY valid JSON, no markdown.`;
      const res1 = await call(p1);
      const parsed1 = JSON.parse(res1.replace(/```json|```/g, "").trim());
      
      // Ensure dimensions array exists
      if (!parsed1.dimensions || !Array.isArray(parsed1.dimensions)) {
        throw new Error('Invalid scorecard structure received');
      }
      
      setScore1(parsed1);
      
      const p2 = `Refine the Dell Technologies supplier scorecard. Adjust to emphasize: Technical Capability to 30%, Quality Performance to 25%, ESG Compliance to 25%, Financial Health to 15%, Innovation Capability to 5%. Add Dell-specific KPIs: "Cybersecurity Certification Status", "Supply Chain Transparency Score", "Carbon Footprint Reduction %" under relevant dimensions. Return same JSON structure with these modifications. Current scorecard: ${JSON.stringify(parsed1)}. Return ONLY valid JSON, no markdown.`;
      const res2 = await call(p2);
      const parsed2 = JSON.parse(res2.replace(/```json|```/g, "").trim());
      
      // Ensure dimensions array exists for refined scorecard
      if (!parsed2.dimensions || !Array.isArray(parsed2.dimensions)) {
        throw new Error('Invalid refined scorecard structure received');
      }
      
      setScore2(parsed2);
    } catch (e) { 
      setError(`Error generating scorecard: ${e.message}`);
      setScore1(null);
      setScore2(null);
    } finally { 
      setLoading(false); 
    }
  };

  const toggleProduct = (product) => {
    setSelectedProducts(prev => 
      prev.includes(product) ? prev.filter(p => p !== product) : [...prev, product]
    );
  };

  const riskColor = (s) => {
    const str = String(s).toLowerCase();
    const n = parseInt(s);
    if (n >= 8 || str.includes('high')) return 'bg-red-100 text-red-800 border-red-300';
    if (n >= 5 || str.includes('medium')) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    return 'bg-green-100 text-green-800 border-green-300';
  };

  const contractColor = (t) => ({ 'FFP': 'bg-blue-600', 'T&M': 'bg-purple-600', 'TM': 'bg-purple-600', 'CR': 'bg-orange-600' }[t] || 'bg-gray-600');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-gradient-to-r from-blue-600 to-cyan-500 rounded-xl shadow-2xl p-6 mb-6">
          <div className="flex items-center gap-4">
            <Building2 size={40} className="text-white" />
            <div>
              <h1 className="text-3xl font-bold text-white">Dell Technologies</h1>
              <p className="text-blue-100">AI-Powered Procurement Intelligence Dashboard</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-xl mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x">
            <button onClick={() => setTask(1)} className={`p-6 transition-all ${task === 1 ? 'bg-blue-50 border-l-4 border-blue-600' : 'hover:bg-gray-50'}`}>
              <div className="flex items-center justify-center mb-2">
                <Search size={32} className={task === 1 ? 'text-blue-600' : 'text-gray-400'} />
              </div>
              <h3 className="font-bold text-center">Task 1</h3>
              <p className="text-sm text-center text-gray-600 mt-1">Market Intelligence</p>
            </button>
            <button onClick={() => setTask(2)} className={`p-6 transition-all ${task === 2 ? 'bg-purple-50 border-l-4 border-purple-600' : 'hover:bg-gray-50'}`}>
              <div className="flex items-center justify-center mb-2">
                <FileText size={32} className={task === 2 ? 'text-purple-600' : 'text-gray-400'} />
              </div>
              <h3 className="font-bold text-center">Task 2</h3>
              <p className="text-sm text-center text-gray-600 mt-1">Contract Selection</p>
            </button>
            <button onClick={() => setTask(3)} className={`p-6 transition-all ${task === 3 ? 'bg-green-50 border-l-4 border-green-600' : 'hover:bg-gray-50'}`}>
              <div className="flex items-center justify-center mb-2">
                <Award size={32} className={task === 3 ? 'text-green-600' : 'text-gray-400'} />
              </div>
              <h3 className="font-bold text-center">Task 3</h3>
              <p className="text-sm text-center text-gray-600 mt-1">Supplier Scorecard</p>
            </button>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-xl p-6">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-r-lg">
              <div className="flex gap-3">
                <AlertCircle className="text-red-500 flex-shrink-0" size={20} />
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          )}

          {task === 1 && (
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Supplier Market Intelligence</h2>
                <p className="text-gray-600 text-sm">Select a category to analyze top suppliers and sourcing risks</p>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-bold text-gray-700 mb-3">Select Product/Service Category</label>
                <div className="relative">
                  <select 
                    value={selectedCategory} 
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg appearance-none cursor-pointer focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-800 font-medium"
                  >
                    <option value="">-- Select a Category --</option>
                    {categories.map((cat, i) => (
                      <option key={i} value={cat}>{cat}</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none" size={20} />
                </div>
              </div>

              <button 
                onClick={doMarket} 
                disabled={loading || !selectedCategory}
                className="w-full md:w-auto px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed font-bold text-lg shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-3"
              >
                {loading ? (
                  <>
                    <Loader className="animate-spin" size={24} />
                    Generating Intelligence...
                  </>
                ) : (
                  <>
                    <Search size={24} />
                    Generate Market Intelligence
                  </>
                )}
              </button>

              {market && (
                <div className="mt-8 space-y-6">
                  {market.marketOverview && (
                    <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border-2 border-blue-200 rounded-xl p-5">
                      <h4 className="font-bold text-blue-900 text-lg mb-2 flex items-center gap-2">
                        <TrendingUp size={20} />
                        Market Overview
                      </h4>
                      <p className="text-gray-700">{market.marketOverview}</p>
                    </div>
                  )}

                  <div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-3 border-b-2 border-gray-200 pb-3">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <TrendingUp className="text-blue-600" size={28} />
                      </div>
                      Top 5 Global Suppliers
                    </h3>
                    <div className="space-y-4">
                      {market.topSuppliers?.map((s, i) => (
                        <div key={i} className="border-2 border-gray-200 rounded-xl p-6 hover:shadow-xl hover:border-blue-300 transition-all bg-gradient-to-r from-white to-blue-50">
                          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-4">
                            <div className="flex gap-4">
                              <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-cyan-600 text-white rounded-xl flex items-center justify-center font-bold text-2xl shadow-lg flex-shrink-0">
                                {s.rank}
                              </div>
                              <div>
                                <h4 className="text-xl font-bold text-gray-800">{s.name}</h4>
                                <p className="text-sm text-gray-600 flex items-center gap-2 mt-1">
                                  <Globe size={16} className="text-blue-600" />
                                  {s.headquarters}
                                </p>
                              </div>
                            </div>
                            <div className="flex flex-col gap-2">
                              {s.marketShare && (
                                <span className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-bold text-center shadow">
                                  {s.marketShare} Market Share
                                </span>
                              )}
                              {s.annualRevenue && (
                                <span className="text-sm text-gray-600 text-center font-medium">{s.annualRevenue}</span>
                              )}
                            </div>
                          </div>

                          <div className="grid md:grid-cols-2 gap-4 mb-4">
                            <div className="bg-white rounded-lg p-4 border border-gray-200">
                              <p className="text-xs font-bold text-gray-700 mb-3 uppercase tracking-wide">Key Capabilities</p>
                              <div className="flex flex-wrap gap-2">
                                {s.keyCapabilities?.map((c, j) => (
                                  <span key={j} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                                    {c}
                                  </span>
                                ))}
                              </div>
                            </div>
                            <div className="bg-white rounded-lg p-4 border border-gray-200">
                              <p className="text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">Differentiators</p>
                              <p className="text-sm text-gray-700">{s.differentiators}</p>
                            </div>
                          </div>

                          {s.dellRelevance && (
                            <div className="bg-blue-600 text-white rounded-lg p-4">
                              <p className="text-xs font-bold mb-2 uppercase tracking-wide">Dell Relevance</p>
                              <p className="text-sm">{s.dellRelevance}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-3 border-b-2 border-gray-200 pb-3">
                      <div className="p-2 bg-orange-100 rounded-lg">
                        <AlertCircle className="text-orange-600" size={28} />
                      </div>
                      Country-Level Sourcing Risks
                    </h3>
                    <div className="space-y-4">
                      {market.countryRisks?.map((r, i) => (
                        <div key={i} className="border-2 border-gray-200 rounded-xl p-6 hover:shadow-xl transition-all">
                          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
                            <div>
                              <h4 className="text-xl font-bold text-gray-800">{r.country}</h4>
                              {r.supplierConcentration && (
                                <p className="text-sm text-gray-600 mt-1">Supplier Concentration: <span className="font-semibold">{r.supplierConcentration}</span></p>
                              )}
                            </div>
                            <span className={`px-4 py-2 rounded-lg text-sm font-bold border-2 ${riskColor(r.overallRiskLevel)}`}>
                              {r.overallRiskLevel} Risk Overall
                            </span>
                          </div>

                          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                            <div className={`p-4 rounded-lg border-2 ${riskColor(r.politicalRisk?.score)}`}>
                              <div className="flex items-center justify-between mb-3">
                                <p className="text-xs font-bold uppercase tracking-wide">Political Risk</p>
                                <span className="text-2xl font-bold">{r.politicalRisk?.score}/10</span>
                              </div>
                              <p className="text-xs mb-2 leading-relaxed">{r.politicalRisk?.assessment}</p>
                              {r.politicalRisk?.keyFactors && r.politicalRisk.keyFactors.length > 0 && (
                                <ul className="text-xs space-y-1 mt-2">
                                  {r.politicalRisk.keyFactors.map((f, j) => (
                                    <li key={j} className="flex items-start gap-1">
                                      <span className="text-red-600 font-bold">•</span>
                                      <span>{f}</span>
                                    </li>
                                  ))}
                                </ul>
                              )}
                            </div>

                            <div className={`p-4 rounded-lg border-2 ${riskColor(r.logisticsRisk?.score)}`}>
                              <div className="flex items-center justify-between mb-3">
                                <p className="text-xs font-bold uppercase tracking-wide">Logistics Risk</p>
                                <span className="text-2xl font-bold">{r.logisticsRisk?.score}/10</span>
                              </div>
                              <p className="text-xs mb-2 leading-relaxed">{r.logisticsRisk?.assessment}</p>
                              {r.logisticsRisk?.keyFactors && r.logisticsRisk.keyFactors.length > 0 && (
                                <ul className="text-xs space-y-1 mt-2">
                                  {r.logisticsRisk.keyFactors.map((f, j) => (
                                    <li key={j} className="flex items-start gap-1">
                                      <span className="text-yellow-600 font-bold">•</span>
                                      <span>{f}</span>
                                    </li>
                                  ))}
                                </ul>
                              )}
                            </div>

                            <div className={`p-4 rounded-lg border-2 ${riskColor(r.complianceRisk?.score)}`}>
                              <div className="flex items-center justify-between mb-3">
                                <p className="text-xs font-bold uppercase tracking-wide">Compliance Risk</p>
                                <span className="text-2xl font-bold">{r.complianceRisk?.score}/10</span>
                              </div>
                              <p className="text-xs mb-2 leading-relaxed">{r.complianceRisk?.assessment}</p>
                              {r.complianceRisk?.keyFactors && r.complianceRisk.keyFactors.length > 0 && (
                                <ul className="text-xs space-y-1 mt-2">
                                  {r.complianceRisk.keyFactors.map((f, j) => (
                                    <li key={j} className="flex items-start gap-1">
                                      <span className="text-orange-600 font-bold">•</span>
                                      <span>{f}</span>
                                    </li>
                                  ))}
                                </ul>
                              )}
                            </div>

                            <div className={`p-4 rounded-lg border-2 ${riskColor(r.esgRisk?.score)}`}>
                              <div className="flex items-center justify-between mb-3">
                                <p className="text-xs font-bold uppercase tracking-wide">ESG Risk</p>
                                <span className="text-2xl font-bold">{r.esgRisk?.score}/10</span>
                              </div>
                              <p className="text-xs mb-2 leading-relaxed">{r.esgRisk?.assessment}</p>
                              {r.esgRisk?.keyFactors && r.esgRisk.keyFactors.length > 0 && (
                                <ul className="text-xs space-y-1 mt-2">
                                  {r.esgRisk.keyFactors.map((f, j) => (
                                    <li key={j} className="flex items-start gap-1">
                                      <span className="text-green-600 font-bold">•</span>
                                      <span>{f}</span>
                                    </li>
                                  ))}
                                </ul>
                              )}
                            </div>
                          </div>

                          {r.mitigation && (
                            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
                              <p className="text-xs font-bold text-blue-900 mb-2 uppercase tracking-wide flex items-center gap-2">
                                <CheckCircle size={16} />
                                Mitigation Strategies
                              </p>
                              <p className="text-sm text-gray-700">{r.mitigation}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {task === 2 && (
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Contract Type Selection</h2>
                <p className="text-gray-600 text-sm">Select products/services to get contract recommendations (FFP, T&M, CR)</p>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-bold text-gray-700 mb-3">
                  Select Dell Products/Services ({selectedProducts.length} selected)
                </label>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-96 overflow-y-auto p-4 border-2 border-gray-300 rounded-lg bg-gray-50">
                  {dellProducts.map((prod, i) => (
                    <label key={i} className="flex items-start gap-3 p-3 bg-white border-2 border-gray-200 rounded-lg cursor-pointer hover:border-purple-400 hover:shadow transition-all">
                      <input
                        type="checkbox"
                        checked={selectedProducts.includes(prod)}
                        onChange={() => toggleProduct(prod)}
                        className="mt-1 w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-500"
                      />
                      <span className="text-sm text-gray-800 font-medium">{prod}</span>
                    </label>
                  ))}
                </div>
              </div>

              <button 
                onClick={doContract} 
                disabled={loading || selectedProducts.length === 0}
                className="w-full md:w-auto px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed font-bold text-lg shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-3"
              >
                {loading ? (
                  <>
                    <Loader className="animate-spin" size={24} />
                    Analyzing Contracts...
                  </>
                ) : (
                  <>
                    <FileText size={24} />
                    Analyze Contract Types
                  </>
                )}
              </button>

              {contract && (
                <div className="mt-8 space-y-6">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-3 border-b-2 border-gray-200 pb-3">
                      <div className="p-2 bg-purple-100 rounded-lg">
                        <FileText className="text-purple-600" size={28} />
                      </div>
                      Contract Recommendations by Category
                    </h3>
                    <div className="space-y-4">
                      {contract.categories?.map((c, i) => (
                        <div key={i} className="border-2 border-gray-200 rounded-xl p-6 hover:shadow-xl transition-all bg-gradient-to-r from-white to-purple-50">
                          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
                            <h4 className="text-lg font-bold text-gray-800">{c.name}</h4>
                            <div className="flex items-center gap-3">
                              <span className={`${contractColor(c.recommendedContract)} text-white px-4 py-2 rounded-lg text-sm font-bold shadow`}>
                                Recommended: {c.recommendedContract}
                              </span>
                              <span className={`px-3 py-1 rounded-lg text-xs font-bold ${c.confidence === 'High' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                                {c.confidence} Confidence
                              </span>
                            </div>
                          </div>

                          <div className="grid md:grid-cols-4 gap-3 mb-4">
                            <div className="bg-white rounded-lg p-3 border border-gray-200">
                              <p className="text-xs text-gray-600 mb-1">Cost Predictability</p>
                              <p className="text-sm font-bold text-gray-800">{c.assessment?.costPredictability}</p>
                              <p className="text-xs text-gray-600 mt-1">{c.assessment?.costPredictabilityReason}</p>
                            </div>
                            <div className="bg-white rounded-lg p-3 border border-gray-200">
                              <p className="text-xs text-gray-600 mb-1">Market Volatility</p>
                              <p className="text-sm font-bold text-gray-800">{c.assessment?.marketVolatility}</p>
                              <p className="text-xs text-gray-600 mt-1">{c.assessment?.marketVolatilityReason}</p>
                            </div>
                            <div className="bg-white rounded-lg p-3 border border-gray-200">
                              <p className="text-xs text-gray-600 mb-1">Duration</p>
                              <p className="text-sm font-bold text-gray-800">{c.assessment?.duration}</p>
                              <p className="text-xs text-gray-600 mt-1">{c.assessment?.durationReason}</p>
                            </div>
                            <div className="bg-white rounded-lg p-3 border border-gray-200">
                              <p className="text-xs text-gray-600 mb-1">Volume</p>
                              <p className="text-sm font-bold text-gray-800">{c.assessment?.volume}</p>
                              <p className="text-xs text-gray-600 mt-1">{c.assessment?.volumeReason}</p>
                            </div>
                          </div>

                          <div className="bg-purple-50 rounded-lg p-4 mb-3 border border-purple-200">
                            <p className="text-xs font-bold text-purple-900 mb-2 uppercase tracking-wide">Justification</p>
                            <p className="text-sm text-gray-700">{c.justification}</p>
                          </div>

                          {c.alternativeOption && (
                            <div className="bg-blue-50 rounded-lg p-4 mb-3 border border-blue-200">
                              <p className="text-xs font-bold text-blue-900 mb-2 uppercase tracking-wide">Alternative Option</p>
                              <p className="text-sm text-gray-700">{c.alternativeOption}</p>
                            </div>
                          )}

                          {c.riskConsiderations && c.riskConsiderations.length > 0 && (
                            <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
                              <p className="text-xs font-bold text-orange-900 mb-2 uppercase tracking-wide">Risk Considerations</p>
                              <ul className="space-y-1">
                                {c.riskConsiderations.map((r, j) => (
                                  <li key={j} className="text-sm text-gray-700 flex items-start gap-2">
                                    <span className="text-orange-600 font-bold">•</span>
                                    <span>{r}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {contract.contractComparison && (
                    <div>
                      <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-3 border-b-2 border-gray-200 pb-3">
                        <div className="p-2 bg-indigo-100 rounded-lg">
                          <BarChart3 className="text-indigo-600" size={28} />
                        </div>
                        Contract Type Comparison
                      </h3>
                      <div className="grid md:grid-cols-3 gap-6">
                        {Object.entries(contract.contractComparison).map(([type, det]) => (
                          <div key={type} className="border-2 border-gray-200 rounded-xl p-5 hover:shadow-xl transition-all bg-white">
                            <div className={`${contractColor(type)} text-white px-4 py-3 rounded-lg inline-block mb-4 shadow-lg`}>
                              <h4 className="font-bold text-lg">{type === 'TM' ? 'T&M' : type}</h4>
                            </div>
                            <p className="text-sm text-gray-600 mb-4 italic">{det.suitability}</p>
                            
                            <div className="mb-4">
                              <p className="text-xs font-bold text-green-700 mb-2 uppercase tracking-wide flex items-center gap-1">
                                <CheckCircle size={14} />
                                Advantages
                              </p>
                              <ul className="space-y-1">
                                {det.advantages?.map((a, i) => (
                                  <li key={i} className="text-xs text-gray-700 flex items-start gap-2">
                                    <span className="text-green-600 font-bold">+</span>
                                    <span>{a}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>

                            <div className="mb-4">
                              <p className="text-xs font-bold text-red-700 mb-2 uppercase tracking-wide flex items-center gap-1">
                                <AlertCircle size={14} />
                                Disadvantages
                              </p>
                              <ul className="space-y-1">
                                {det.disadvantages?.map((d, i) => (
                                  <li key={i} className="text-xs text-gray-700 flex items-start gap-2">
                                    <span className="text-red-600 font-bold">−</span>
                                    <span>{d}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>

                            {det.dellExamples && det.dellExamples.length > 0 && (
                              <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                                <p className="text-xs font-bold text-blue-900 mb-2 uppercase tracking-wide">Dell Examples</p>
                                <ul className="space-y-1">
                                  {det.dellExamples.map((ex, i) => (
                                    <li key={i} className="text-xs text-gray-700">• {ex}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {contract.procurementRecommendations && contract.procurementRecommendations.length > 0 && (
                    <div className="bg-gradient-to-r from-green-50 to-teal-50 border-2 border-green-200 rounded-xl p-6">
                      <h3 className="text-xl font-bold text-green-900 mb-4 flex items-center gap-2">
                        <CheckCircle size={24} />
                        Overall Procurement Recommendations
                      </h3>
                      <ul className="space-y-2">
                        {contract.procurementRecommendations.map((rec, i) => (
                          <li key={i} className="flex items-start gap-3 text-gray-700">
                            <span className="font-bold text-green-600 text-lg">{i + 1}.</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {task === 3 && (
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Supplier Evaluation Scorecard</h2>
                <p className="text-gray-600 text-sm">Comprehensive evaluation framework tailored for Dell Technologies</p>
              </div>

              <button 
                onClick={doScorecard} 
                disabled={loading || (score1 && score2)}
                className="w-full md:w-auto px-8 py-4 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed font-bold text-lg shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-3 mb-8"
              >
                {loading ? (
                  <>
                    <Loader className="animate-spin" size={24} />
                    Generating Scorecards...
                  </>
                ) : (score1 && score2) ? (
                  <>
                    <CheckCircle size={24} />
                    Scorecards Generated
                  </>
                ) : (
                  <>
                    <Award size={24} />
                    Generate Supplier Scorecards
                  </>
                )}
              </button>

              {score1 && (
                <div className="space-y-8">
                  <div>
                    <div className="bg-gradient-to-r from-green-50 to-teal-50 border-2 border-green-200 rounded-xl p-6 mb-6">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-3 bg-green-600 rounded-lg">
                          <Award className="text-white" size={32} />
                        </div>
                        <div>
                          <h3 className="text-2xl font-bold text-green-900">Initial AI-Generated Scorecard</h3>
                          <p className="text-green-800 text-sm mt-1">
                            Organization: {score1.organization} | Category: {score1.category} | Industry: {score1.industry}
                          </p>
                        </div>
                      </div>
                      <div className="grid md:grid-cols-3 gap-4 mt-4">
                        <div className="bg-white rounded-lg p-4 border border-green-200">
                          <p className="text-xs text-green-700 font-bold mb-1">Total Score</p>
                          <p className="text-3xl font-bold text-green-900">{score1.totalMaxScore}</p>
                        </div>
                        <div className="bg-white rounded-lg p-4 border border-green-200">
                          <p className="text-xs text-green-700 font-bold mb-1">Dimensions</p>
                          <p className="text-3xl font-bold text-green-900">{score1.dimensions?.length || 5}</p>
                        </div>
                        <div className="bg-white rounded-lg p-4 border border-green-200">
                          <p className="text-xs text-green-700 font-bold mb-1">Generated</p>
                          <p className="text-sm font-bold text-green-900">{score1.generatedDate}</p>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {score1.dimensions?.map((d, i) => (
                        <div key={i} className="border-2 border-gray-200 rounded-xl p-6 hover:shadow-xl transition-all bg-white">
                          <div className="flex items-center justify-between mb-4 pb-4 border-b-2 border-gray-100">
                            <div>
                              <h4 className="text-xl font-bold text-gray-800">{d.name}</h4>
                              <p className="text-sm text-gray-600 mt-1">{d.description}</p>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="px-4 py-2 bg-green-600 text-white rounded-lg text-lg font-bold shadow">
                                {d.weight}%
                              </span>
                            </div>
                          </div>

                          <div className="space-y-3">
                            {d.kpis?.map((k, j) => (
                              <div key={j} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                                <div className="flex items-start justify-between mb-3">
                                  <h5 className="font-bold text-gray-800">{k.name}</h5>
                                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-lg text-xs font-bold">
                                    Max: {k.maxScore} pts
                                  </span>
                                </div>
                                <p className="text-sm text-gray-600 mb-2">{k.description}</p>
                                <div className="grid md:grid-cols-2 gap-3 mb-3">
                                  <div className="bg-white rounded p-3 border border-gray-200">
                                    <p className="text-xs font-bold text-gray-700 mb-1">Measurement</p>
                                    <p className="text-xs text-gray-600">{k.measurement}</p>
                                  </div>
                                  <div className="bg-white rounded p-3 border border-gray-200">
                                    <p className="text-xs font-bold text-gray-700 mb-1">Target</p>
                                    <p className="text-xs text-gray-600">{k.target}</p>
                                  </div>
                                </div>
                                {k.scoringCriteria && (
                                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                                    <div className="bg-green-50 rounded p-2 border border-green-200">
                                      <p className="text-xs font-bold text-green-800 mb-1">Excellent</p>
                                      <p className="text-xs text-gray-600">{k.scoringCriteria.excellent}</p>
                                    </div>
                                    <div className="bg-blue-50 rounded p-2 border border-blue-200">
                                      <p className="text-xs font-bold text-blue-800 mb-1">Good</p>
                                      <p className="text-xs text-gray-600">{k.scoringCriteria.good}</p>
                                    </div>
                                    <div className="bg-yellow-50 rounded p-2 border border-yellow-200">
                                      <p className="text-xs font-bold text-yellow-800 mb-1">Acceptable</p>
                                      <p className="text-xs text-gray-600">{k.scoringCriteria.acceptable}</p>
                                    </div>
                                    <div className="bg-red-50 rounded p-2 border border-red-200">
                                      <p className="text-xs font-bold text-red-800 mb-1">Poor</p>
                                      <p className="text-xs text-gray-600">{k.scoringCriteria.poor}</p>
                                    </div>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>

                    {score1.overallScoringGuide && (
                      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-xl p-6">
                        <h4 className="text-lg font-bold text-indigo-900 mb-4">Overall Scoring Guide</h4>
                        <div className="grid md:grid-cols-2 gap-4">
                          {Object.entries(score1.overallScoringGuide).map(([level, desc]) => (
                            <div key={level} className="bg-white rounded-lg p-4 border-2 border-indigo-200">
                              <p className="font-bold text-indigo-900 capitalize mb-2">{level}</p>
                              <p className="text-sm text-gray-700">{desc}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {score2 && (
                    <div>
                      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-6 mb-6">
                        <div className="flex items-center gap-3 mb-3">
                          <div className="p-3 bg-blue-600 rounded-lg">
                            <CheckCircle className="text-white" size={32} />
                          </div>
                          <div>
                            <h3 className="text-2xl font-bold text-blue-900">Refined Dell-Specific Scorecard</h3>
                            <p className="text-blue-800 text-sm mt-1">
                              Customized with adjusted weightages and Dell-specific KPIs
                            </p>
                          </div>
                        </div>
                        <div className="bg-blue-100 border border-blue-300 rounded-lg p-4 mt-4">
                          <p className="text-sm text-blue-900 font-semibold mb-2">Key Refinements Applied:</p>
                          <ul className="text-sm text-blue-800 space-y-1">
                            <li>• Emphasis on Technical Capability and Quality Performance</li>
                            <li>• Enhanced ESG Compliance focus</li>
                            <li>• Dell-specific KPIs: Cybersecurity, Supply Chain Transparency, Carbon Footprint</li>
                          </ul>
                        </div>
                      </div>

                      <div className="space-y-4">
                        {score2.dimensions?.map((d, i) => (
                          <div key={i} className="border-2 border-blue-200 rounded-xl p-6 hover:shadow-xl transition-all bg-gradient-to-r from-white to-blue-50">
                            <div className="flex items-center justify-between mb-4 pb-4 border-b-2 border-blue-100">
                              <div>
                                <h4 className="text-xl font-bold text-gray-800">{d.name}</h4>
                                <p className="text-sm text-gray-600 mt-1">{d.description}</p>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className="px-4 py-2 bg-blue-600 text-white rounded-lg text-lg font-bold shadow">
                                  {d.weight}%
                                </span>
                              </div>
                            </div>

                            <div className="space-y-3">
                              {d.kpis?.map((k, j) => (
                                <div key={j} className="bg-white rounded-lg p-4 border-2 border-blue-200">
                                  <div className="flex items-start justify-between mb-3">
                                    <h5 className="font-bold text-gray-800">{k.name}</h5>
                                    <span className="px-3 py-1 bg-blue-600 text-white rounded-lg text-xs font-bold">
                                      Max: {k.maxScore} pts
                                    </span>
                                  </div>
                                  <p className="text-sm text-gray-600 mb-2">{k.description}</p>
                                  <div className="grid md:grid-cols-2 gap-3 mb-3">
                                    <div className="bg-blue-50 rounded p-3 border border-blue-200">
                                      <p className="text-xs font-bold text-blue-700 mb-1">Measurement</p>
                                      <p className="text-xs text-gray-600">{k.measurement}</p>
                                    </div>
                                    <div className="bg-blue-50 rounded p-3 border border-blue-200">
                                      <p className="text-xs font-bold text-blue-700 mb-1">Target</p>
                                      <p className="text-xs text-gray-600">{k.target}</p>
                                    </div>
                                  </div>
                                  {k.scoringCriteria && (
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                                      <div className="bg-green-50 rounded p-2 border border-green-300">
                                        <p className="text-xs font-bold text-green-800 mb-1">Excellent</p>
                                        <p className="text-xs text-gray-600">{k.scoringCriteria.excellent}</p>
                                      </div>
                                      <div className="bg-blue-50 rounded p-2 border border-blue-300">
                                        <p className="text-xs font-bold text-blue-800 mb-1">Good</p>
                                        <p className="text-xs text-gray-600">{k.scoringCriteria.good}</p>
                                      </div>
                                      <div className="bg-yellow-50 rounded p-2 border border-yellow-300">
                                        <p className="text-xs font-bold text-yellow-800 mb-1">Acceptable</p>
                                        <p className="text-xs text-gray-600">{k.scoringCriteria.acceptable}</p>
                                      </div>
                                      <div className="bg-red-50 rounded p-2 border border-red-300">
                                        <p className="text-xs font-bold text-red-800 mb-1">Poor</p>
                                        <p className="text-xs text-gray-600">{k.scoringCriteria.poor}</p>
                                      </div>
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>

                      {score2.recommendations && score2.recommendations.length > 0 && (
                        <div className="bg-gradient-to-r from-green-50 to-teal-50 border-2 border-green-200 rounded-xl p-6">
                          <h4 className="text-lg font-bold text-green-900 mb-4 flex items-center gap-2">
                            <CheckCircle size={24} />
                            Implementation Recommendations
                          </h4>
                          <ul className="space-y-2">
                            {score2.recommendations.map((rec, i) => (
                              <li key={i} className="flex items-start gap-3 text-gray-700">
                                <span className="font-bold text-green-600 text-lg">{i + 1}.</span>
                                <span>{rec}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DellDashboard;
