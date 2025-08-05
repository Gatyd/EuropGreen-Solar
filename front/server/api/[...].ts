import { joinURL } from "ufo";

export default defineEventHandler(async (event) => {
	const proxyUrl = useRuntimeConfig().proxyUrl;

	const path = event.path.replace(/^\/api\//, "");
	const target = joinURL(proxyUrl, path);

	console.log("THERE IS THE PROXY URL");

	return proxyRequest(event, target);
});
