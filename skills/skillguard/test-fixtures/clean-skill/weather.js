// Simple weather lookup - clean example
const WEATHER_API = 'https://wttr.in';

export async function getWeather(location) {
  const response = await fetch(`${WEATHER_API}/${encodeURIComponent(location)}?format=j1`);
  const data = await response.json();
  return {
    location: data.nearest_area?.[0]?.areaName?.[0]?.value,
    temp_c: data.current_condition?.[0]?.temp_C,
    temp_f: data.current_condition?.[0]?.temp_F,
    condition: data.current_condition?.[0]?.weatherDesc?.[0]?.value,
  };
}
