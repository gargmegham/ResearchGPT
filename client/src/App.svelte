<script>
	import { Router, Route } from 'svelte-routing';
	import Home from '$lib/pages/Home.svelte';
	import Assisstant from '$lib/pages/Assisstant.svelte';
</script>

<Router>
	<Route path="/v2/query" component={Home} />
	<Route path="/v2/query/chatroom/:search/:title" component={Assisstant} />
</Router>
