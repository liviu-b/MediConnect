/**
 * Romanian counties (județe) with their cities
 * Organized hierarchically: County → Cities
 */
export const ROMANIAN_COUNTIES_WITH_CITIES = {
  "Alba": ["Alba Iulia", "Aiud", "Blaj", "Sebeș", "Cugir"],
  "Arad": ["Arad", "Ineu", "Chișineu-Criș", "Curtici", "Lipova"],
  "Argeș": ["Pitești", "Câmpulung", "Curtea de Argeș", "Mioveni", "Costești"],
  "Bacău": ["Bacău", "Onești", "Moinești", "Comănești", "Buhuși"],
  "Bihor": ["Oradea", "Salonta", "Beiuș", "Marghita", "Aleșd"],
  "Bistrița-Năsăud": ["Bistrița", "Beclean", "Năsăud", "Sângeorz-Băi"],
  "Botoșani": ["Botoșani", "Dorohoi", "Darabani", "Săveni", "Flămânzi"],
  "Brașov": ["Brașov", "Făgăraș", "Săcele", "Codlea", "Zărnești", "Predeal"],
  "Brăila": ["Brăila", "Ianca", "Însurăței", "Făurei"],
  "București": ["București", "Sectorul 1", "Sectorul 2", "Sectorul 3", "Sectorul 4", "Sectorul 5", "Sectorul 6"],
  "Buzău": ["Buzău", "Râmnicu Sărat", "Nehoiu", "Pogoanele"],
  "Caraș-Severin": ["Reșița", "Caransebeș", "Bocșa", "Moldova Nouă", "Oravița"],
  "Călărași": ["Călărași", "Oltenița", "Lehliu Gară", "Budești"],
  "Cluj": ["Cluj-Napoca", "Turda", "Dej", "Gherla", "Câmpia Turzii", "Huedin"],
  "Constanța": ["Constanța", "Mangalia", "Medgidia", "Năvodari", "Cernavodă", "Eforie"],
  "Covasna": ["Sfântu Gheorghe", "Târgu Secuiesc", "Covasna", "Întorsura Buzăului"],
  "Dâmbovița": ["Târgoviște", "Moreni", "Pucioasa", "Găești", "Titu"],
  "Dolj": ["Craiova", "Băilești", "Calafat", "Filiași", "Segarcea"],
  "Galați": ["Galați", "Tecuci", "Târgu Bujor", "Berești"],
  "Giurgiu": ["Giurgiu", "Bolintin-Vale", "Mihăilești"],
  "Gorj": ["Târgu Jiu", "Motru", "Rovinari", "Târgu Cărbunești", "Novaci"],
  "Harghita": ["Miercurea Ciuc", "Odorheiu Secuiesc", "Gheorgheni", "Toplița", "Cristuru Secuiesc"],
  "Hunedoara": ["Deva", "Hunedoara", "Petroșani", "Lupeni", "Vulcan", "Orăștiea", "Brad"],
  "Ialomița": ["Slobozia", "Fetești", "Urziceni", "Țăndărei", "Fierbinți-Târg"],
  "Iași": ["Iași", "Pașcani", "Hârlău", "Târgu Frumos", "Podu Iloaiei"],
  "Ilfov": ["Buftea", "Voluntari", "Pantelimon", "Popești-Leordeni", "Chitila", "Otopeni", "Bragadiru"],
  "Maramureș": ["Baia Mare", "Sighetu Marmației", "Borșa", "Vișeu de Sus", "Târgu Lăpuș"],
  "Mehedinți": ["Drobeta-Turnu Severin", "Orșova", "Strehaia", "Vânju Mare"],
  "Mureș": ["Târgu Mureș", "Reghin", "Sighișoara", "Târnăveni", "Luduș"],
  "Neamț": ["Piatra Neamț", "Roman", "Târgu Neamț", "Bicaz", "Roznov"],
  "Olt": ["Slatina", "Caracal", "Balș", "Corabia", "Scornicești"],
  "Prahova": ["Ploiești", "Câmpina", "Băicoi", "Mizil", "Vălenii de Munte", "Sinaia", "Azuga", "Bușteni"],
  "Satu Mare": ["Satu Mare", "Carei", "Negrești-Oaș", "Tășnad", "Livada"],
  "Sălaj": ["Zalău", "Șimleu Silvaniei", "Jibou", "Cehu Silvaniei"],
  "Sibiu": ["Sibiu", "Mediaș", "Cisnădie", "Agnita", "Avrig", "Copșa Mică"],
  "Suceava": ["Suceava", "Fălticeni", "Rădăuți", "Câmpulung Moldovenesc", "Vatra Dornei", "Gura Humorului"],
  "Teleorman": ["Alexandria", "Roșiorii de Vede", "Turnu Măgurele", "Zimnicea", "Videle"],
  "Timiș": ["Timișoara", "Lugoj", "Sânnicolau Mare", "Jimbolia", "Făget", "Buziaș"],
  "Tulcea": ["Tulcea", "Babadag", "Măcin", "Isaccea", "Sulina"],
  "Vaslui": ["Vaslui", "Bârlad", "Huși", "Murgeni", "Negrești"],
  "Vâlcea": ["Râmnicu Vâlcea", "Drăgășani", "Băile Olănești", "Călimănești", "Horezu", "Brezoi"],
  "Vrancea": ["Focșani", "Adjud", "Mărășești", "Odobești", "Panciu"]
};

/**
 * Get all counties (județe) as an array
 */
export const ROMANIAN_COUNTIES = Object.keys(ROMANIAN_COUNTIES_WITH_CITIES).sort();

/**
 * Get cities for a specific county
 */
export const getCitiesForCounty = (county) => {
  return ROMANIAN_COUNTIES_WITH_CITIES[county] || [];
};

/**
 * Get all cities (flat list)
 */
export const getAllCities = () => {
  const cities = [];
  Object.values(ROMANIAN_COUNTIES_WITH_CITIES).forEach(countyCities => {
    cities.push(...countyCities);
  });
  return cities.sort();
};
