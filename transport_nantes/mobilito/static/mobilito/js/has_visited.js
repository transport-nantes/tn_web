document.addEventListener('DOMContentLoaded', () => {
    const hasVisited = () => {
        const visited = localStorage.getItem('visited');
        if (visited) {
            return true;
        }
        localStorage.setItem('visited', 'true');
        return false;
    }

    if (hasVisited()) {
        document.getElementById('already-visited').classList.toggle('d-none');
    }
})
