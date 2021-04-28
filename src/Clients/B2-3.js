// MikeDEV's CloudLink API Suite
// This extension combines the CloudLink API, the CloudCoin API, and the CloudDisk API in an all-in-one solution.
// Original Source Code built upon KingdomPi's Scratch-websockets repo.
// See https://github.com/KingdomPy/scratch_websockets/blob/master/index.js for the original script!
// DO NOT USE ON OLDER WEB BROWSERS! CloudLink is designed to run best on a modern web browser.

const vers = 'B2.3'; // Suite version number
const defIP = "ws://127.0.0.1:3000/"; // Default IP address
const testIP = "wss://ef4e5a473455.ngrok.io/"; // Public test server IP.
const enableSpecialHandshake = true; // Experimental direct-linking mode support. 

console.log("[CloudLink Suite] Loading 1/3: Initializing the extension...")

// CloudLink block and icon dataURIs
const cl_block_icon = 'data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI2OS43NjY3MSIgaGVpZ2h0PSI1MS41Mzk5NCIgdmlld0JveD0iMCwwLDY5Ljc2NjcxLDUxLjUzOTk0Ij48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMjA1LjExNjY1LC0xNTQuMjMwMDMpIj48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtpc1BhaW50aW5nTGF5ZXImcXVvdDs6dHJ1ZX0iIGZpbGwtcnVsZT0ibm9uemVybyIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLW1pdGVybGltaXQ9IjEwIiBzdHJva2UtZGFzaGFycmF5PSIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBzdHlsZT0ibWl4LWJsZW5kLW1vZGU6IG5vcm1hbCI+PHBhdGggZD0iTTI3Mi44ODMzNiwxODguODA3NTJjMCw4LjI2MzUzIC02LjY5ODkxLDE0Ljk2MjQ0IC0xNC45NjI0NCwxNC45NjI0NGgtMjYuOTMyMzljLTEyLjQ0MzE3LDAuMDA5MjggLTIyLjgxODksLTkuNTE1NDggLTIzLjg3MTg4LC0yMS45MTQwM2MtMS4wNTI5OCwtMTIuMzk4NTUgNy41Njc5MywtMjMuNTM2NjUgMTkuODM0NDUsLTI1LjYyNTljMTIuMjY2NTIsLTIuMDg5MjUgMjQuMDg4NDksNS41NjcgMjcuMTk5MjksMTcuNjE1MDVoMy43NzA1M2M4LjI2MzUzLDAgMTQuOTYyNDQsNi42OTg5MSAxNC45NjI0NCwxNC45NjI0NHoiIGRhdGEtcGFwZXItZGF0YT0ieyZxdW90O29yaWdQb3MmcXVvdDs6bnVsbH0iIGZpbGw9IiMwNTRjNjMiLz48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtvcmlnUG9zJnF1b3Q7Om51bGx9IiBmaWxsPSJub25lIj48cGF0aCBkPSJNMjIxLjcxODI0LDE4MC44NjkxN2M1LjY2NjIxLC00LjcxOTU0IDEzLjg5NDUzLC00LjcxOTU0IDE5LjU2MDc0LDAiLz48cGF0aCBkPSJNMjE2Ljc0NDcsMTc1LjkzNzMxYzguNDAwMTEsLTcuNDA0NDYgMjAuOTk2NTYsLTcuNDA0NDYgMjkuMzk2NjgsMCIvPjxwYXRoIGQ9Ik0yMjYuNjIyMzIsMTg1LjgxNDkzYzIuODkwODEsLTIuMDUzNzggNi43NjQ1MywtMi4wNTM3OCA5LjY1NTM0LDAiLz48cGF0aCBkPSJNMjMxLjQ1NjkzLDE5MS4yMTkxNGgtMC4wMTM4OSIvPjwvZz48L2c+PC9nPjwvc3ZnPg==';
const cl_menu_icon = 'data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI0OC45OTk3NSIgaGVpZ2h0PSI0OC45OTk3NSIgdmlld0JveD0iMCwwLDQ4Ljk5OTc1LDQ4Ljk5OTc1Ij48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMjE1LjUwMDEyLC0xNTUuNTAwMTIpIj48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtpc1BhaW50aW5nTGF5ZXImcXVvdDs6dHJ1ZX0iIGZpbGwtcnVsZT0ibm9uemVybyIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc3Ryb2tlLWRhc2hhcnJheT0iIiBzdHJva2UtZGFzaG9mZnNldD0iMCIgc3R5bGU9Im1peC1ibGVuZC1tb2RlOiBub3JtYWwiPjxwYXRoIGQ9Ik0yMTcuNTAwMTMsMTgwYzAsLTEyLjQyNjM0IDEwLjA3MzUzLC0yMi40OTk4OCAyMi40OTk4OCwtMjIuNDk5ODhjMTIuNDI2MzQsMCAyMi40OTk4NywxMC4wNzM1MyAyMi40OTk4NywyMi40OTk4OGMwLDEyLjQyNjM0IC0xMC4wNzM1MywyMi40OTk4OCAtMjIuNDk5ODcsMjIuNDk5ODhjLTEyLjQyNjM0LDAgLTIyLjQ5OTg4LC0xMC4wNzM1MyAtMjIuNDk5ODgsLTIyLjQ5OTg4eiIgZGF0YS1wYXBlci1kYXRhPSJ7JnF1b3Q7b3JpZ1BvcyZxdW90OzpudWxsfSIgZmlsbD0iIzA1NGM2MyIgc3Ryb2tlLWxpbmVjYXA9ImJ1dHQiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiLz48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtvcmlnUG9zJnF1b3Q7Om51bGx9IiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMzAuMjc1MiwxODAuMDY3NjJjNS42NjYyMSwtNC43MTk1NCAxMy44OTQ1MywtNC43MTk1NCAxOS41NjA3NCwwIi8+PHBhdGggZD0iTTIyNS4zMDE2NiwxNzUuMTM1NzZjOC40MDAxMSwtNy40MDQ0NiAyMC45OTY1NiwtNy40MDQ0NiAyOS4zOTY2OCwwIi8+PHBhdGggZD0iTTIzNS4xNzkyOCwxODUuMDEzMzhjMi44OTA4MSwtMi4wNTM3OCA2Ljc2NDUzLC0yLjA1Mzc4IDkuNjU1MzQsMCIvPjxwYXRoIGQ9Ik0yNDAuMDEzODksMTkwLjQxNzU5aC0wLjAxMzg5Ii8+PC9nPjwvZz48L2c+PC9zdmc+';

// CloudAccount block and icon dataURIs
const ca_block_icon = 'data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI2OS43NjY3MSIgaGVpZ2h0PSI1MS41Mzk5NCIgdmlld0JveD0iMCwwLDY5Ljc2NjcxLDUxLjUzOTk0Ij48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMjA1LjExNjY1LC0xNTQuMjMwMDMpIj48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtpc1BhaW50aW5nTGF5ZXImcXVvdDs6dHJ1ZX0iIGZpbGwtcnVsZT0ibm9uemVybyIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLW1pdGVybGltaXQ9IjEwIiBzdHJva2UtZGFzaGFycmF5PSIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBzdHlsZT0ibWl4LWJsZW5kLW1vZGU6IG5vcm1hbCI+PHBhdGggZD0iTTI3Mi44ODMzNiwxODguODA3NTJjMCw4LjI2MzUzIC02LjY5ODkxLDE0Ljk2MjQ0IC0xNC45NjI0NCwxNC45NjI0NGgtMjYuOTMyMzljLTEyLjQ0MzE3LDAuMDA5MjggLTIyLjgxODksLTkuNTE1NDggLTIzLjg3MTg4LC0yMS45MTQwM2MtMS4wNTI5OCwtMTIuMzk4NTUgNy41Njc5MywtMjMuNTM2NjUgMTkuODM0NDUsLTI1LjYyNTljMTIuMjY2NTIsLTIuMDg5MjUgMjQuMDg4NDksNS41NjcgMjcuMTk5MjksMTcuNjE1MDVoMy43NzA1M2M4LjI2MzUzLDAgMTQuOTYyNDQsNi42OTg5MSAxNC45NjI0NCwxNC45NjI0NHoiIGRhdGEtcGFwZXItZGF0YT0ieyZxdW90O29yaWdQb3MmcXVvdDs6bnVsbH0iIGZpbGw9IiMwNTRjNjMiLz48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtvcmlnUG9zJnF1b3Q7Om51bGx9IiBmaWxsPSJub25lIj48cGF0aCBkPSJNMjIwLjM5NDgsMTkxLjkzMDkydi0yLjY1MTMxYzAsLTIuOTI4NTYgMi4zNzQwNywtNS4zMDI2MyA1LjMwMjYzLC01LjMwMjYzaDEwLjYwNTI1YzIuOTI4NTYsMCA1LjMwMjYzLDIuMzc0MDcgNS4zMDI2Myw1LjMwMjYzdjIuNjUxMzEiLz48cGF0aCBkPSJNMjI1LjY5NzQzLDE3My4zNzE3M2MwLC0yLjkyODU2IDIuMzc0MDYsLTUuMzAyNjIgNS4zMDI2MiwtNS4zMDI2MmMyLjkyODU2LDAgNS4zMDI2MywyLjM3NDA2IDUuMzAyNjMsNS4zMDI2MmMwLDIuOTI4NTYgLTIuMzc0MDcsNS4zMDI2MyAtNS4zMDI2Myw1LjMwMjYzYy0yLjkyODU2LDAgLTUuMzAyNjIsLTIuMzc0MDcgLTUuMzAyNjIsLTUuMzAyNjN6Ii8+PC9nPjwvZz48L2c+PC9zdmc+';
const ca_menu_icon = 'data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI0OC45OTk3NSIgaGVpZ2h0PSI0OC45OTk3NiIgdmlld0JveD0iMCwwLDQ4Ljk5OTc1LDQ4Ljk5OTc2Ij48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMjE1LjUwMDE0LC0xNTUuNTAwMTMpIj48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtpc1BhaW50aW5nTGF5ZXImcXVvdDs6dHJ1ZX0iIGZpbGwtcnVsZT0ibm9uemVybyIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc3Ryb2tlLWRhc2hhcnJheT0iIiBzdHJva2UtZGFzaG9mZnNldD0iMCIgc3R5bGU9Im1peC1ibGVuZC1tb2RlOiBub3JtYWwiPjxwYXRoIGQ9Ik0yMTcuNTAwMTUsMTgwLjAwMDAyYzAsLTEyLjQyNjM0IDEwLjA3MzUzLC0yMi40OTk4OCAyMi40OTk4OCwtMjIuNDk5ODhjMTIuNDI2MzQsMCAyMi40OTk4NywxMC4wNzM1MyAyMi40OTk4NywyMi40OTk4OGMwLDEyLjQyNjM0IC0xMC4wNzM1MywyMi40OTk4OCAtMjIuNDk5ODcsMjIuNDk5ODhjLTEyLjQyNjM0LDAgLTIyLjQ5OTg4LC0xMC4wNzM1MyAtMjIuNDk5ODgsLTIyLjQ5OTg4eiIgZGF0YS1wYXBlci1kYXRhPSJ7JnF1b3Q7b3JpZ1BvcyZxdW90OzpudWxsfSIgZmlsbD0iIzA1NGM2MyIgc3Ryb2tlLWxpbmVjYXA9ImJ1dHQiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiLz48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtvcmlnUG9zJnF1b3Q7Om51bGx9IiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMjkuMzk0NzUsMTkxLjkzMDkxdi0yLjY1MTMxYzAsLTIuOTI4NTYgMi4zNzQwNywtNS4zMDI2MyA1LjMwMjYzLC01LjMwMjYzaDEwLjYwNTI1YzIuOTI4NTYsMCA1LjMwMjYzLDIuMzc0MDcgNS4zMDI2Myw1LjMwMjYzdjIuNjUxMzEiLz48cGF0aCBkPSJNMjM0LjY5NzM4LDE3My4zNzE3MmMwLC0yLjkyODU2IDIuMzc0MDYsLTUuMzAyNjIgNS4zMDI2MiwtNS4zMDI2MmMyLjkyODU2LDAgNS4zMDI2MywyLjM3NDA2IDUuMzAyNjMsNS4zMDI2MmMwLDIuOTI4NTYgLTIuMzc0MDcsNS4zMDI2MyAtNS4zMDI2Myw1LjMwMjYzYy0yLjkyODU2LDAgLTUuMzAyNjIsLTIuMzc0MDcgLTUuMzAyNjIsLTUuMzAyNjN6Ii8+PC9nPjwvZz48L2c+PC9zdmc+';

// CloudCoin block and icon dataURIs
const cc_block_icon = 'data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI2OS43NjY3MSIgaGVpZ2h0PSI1MS41Mzk5NCIgdmlld0JveD0iMCwwLDY5Ljc2NjcxLDUxLjUzOTk0Ij48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMjA1LjExNjY1LC0xNTQuMjMwMDMpIj48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtpc1BhaW50aW5nTGF5ZXImcXVvdDs6dHJ1ZX0iIGZpbGwtcnVsZT0ibm9uemVybyIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLW1pdGVybGltaXQ9IjEwIiBzdHJva2UtZGFzaGFycmF5PSIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBzdHlsZT0ibWl4LWJsZW5kLW1vZGU6IG5vcm1hbCI+PHBhdGggZD0iTTI3Mi44ODMzNiwxODguODA3NTJjMCw4LjI2MzUzIC02LjY5ODkxLDE0Ljk2MjQ0IC0xNC45NjI0NCwxNC45NjI0NGgtMjYuOTMyMzljLTEyLjQ0MzE3LDAuMDA5MjggLTIyLjgxODksLTkuNTE1NDggLTIzLjg3MTg4LC0yMS45MTQwM2MtMS4wNTI5OCwtMTIuMzk4NTUgNy41Njc5MywtMjMuNTM2NjUgMTkuODM0NDUsLTI1LjYyNTljMTIuMjY2NTIsLTIuMDg5MjUgMjQuMDg4NDksNS41NjcgMjcuMTk5MjksMTcuNjE1MDVoMy43NzA1M2M4LjI2MzUzLDAgMTQuOTYyNDQsNi42OTg5MSAxNC45NjI0NCwxNC45NjI0NHoiIGRhdGEtcGFwZXItZGF0YT0ieyZxdW90O29yaWdQb3MmcXVvdDs6bnVsbH0iIGZpbGw9IiMwNTRjNjMiLz48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtvcmlnUG9zJnF1b3Q7Om51bGx9IiBmaWxsPSJub25lIj48cGF0aCBkPSJNMjMwLjU3ODE1LDE2NC41NTgzMXYzMC45MTg4OSIvPjxwYXRoIGQ9Ik0yMzcuNjA1MTgsMTcwLjE3OTkyaC0xMC41NDA1M2MtMi43MTY2NSwwIC00LjkxODkxLDIuMjAyMjcgLTQuOTE4OTEsNC45MTg5MWMwLDIuNzE2NjUgMi4yMDIyNyw0LjkxODkxIDQuOTE4OTEsNC45MTg5MWg3LjAyNzAyYzIuNzE2NjUsMCA0LjkxODkxLDIuMjAyMjcgNC45MTg5MSw0LjkxODkxYzAsMi43MTY2NSAtMi4yMDIyNyw0LjkxODkxIC00LjkxODkxLDQuOTE4OTFoLTExLjk0NTk0Ii8+PC9nPjwvZz48L2c+PC9zdmc+';
const cc_menu_icon = 'data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI0OC45OTk3NSIgaGVpZ2h0PSI0OC45OTk3NSIgdmlld0JveD0iMCwwLDQ4Ljk5OTc1LDQ4Ljk5OTc1Ij48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMjE1LjUwMDEyLC0xNTUuNTAwMTIpIj48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtpc1BhaW50aW5nTGF5ZXImcXVvdDs6dHJ1ZX0iIGZpbGwtcnVsZT0ibm9uemVybyIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc3Ryb2tlLWRhc2hhcnJheT0iIiBzdHJva2UtZGFzaG9mZnNldD0iMCIgc3R5bGU9Im1peC1ibGVuZC1tb2RlOiBub3JtYWwiPjxwYXRoIGQ9Ik0yMTcuNTAwMTMsMTgwYzAsLTEyLjQyNjM0IDEwLjA3MzUzLC0yMi40OTk4OCAyMi40OTk4OCwtMjIuNDk5ODhjMTIuNDI2MzQsMCAyMi40OTk4NywxMC4wNzM1MyAyMi40OTk4NywyMi40OTk4OGMwLDEyLjQyNjM0IC0xMC4wNzM1MywyMi40OTk4OCAtMjIuNDk5ODcsMjIuNDk5ODhjLTEyLjQyNjM0LDAgLTIyLjQ5OTg4LC0xMC4wNzM1MyAtMjIuNDk5ODgsLTIyLjQ5OTg4eiIgZGF0YS1wYXBlci1kYXRhPSJ7JnF1b3Q7b3JpZ1BvcyZxdW90OzpudWxsfSIgZmlsbD0iIzA1NGM2MyIgc3Ryb2tlLWxpbmVjYXA9ImJ1dHQiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiLz48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtvcmlnUG9zJnF1b3Q7Om51bGx9IiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yNDAsMTY0LjU0MDU1djMwLjkxODg5Ii8+PHBhdGggZD0iTTI0Ny4wMjcwMiwxNzAuMTYyMTdoLTEwLjU0MDUzYy0yLjcxNjY1LDAgLTQuOTE4OTEsMi4yMDIyNyAtNC45MTg5MSw0LjkxODkxYzAsMi43MTY2NSAyLjIwMjI3LDQuOTE4OTEgNC45MTg5MSw0LjkxODkxaDcuMDI3MDJjMi43MTY2NSwwIDQuOTE4OTEsMi4yMDIyNyA0LjkxODkxLDQuOTE4OTFjMCwyLjcxNjY1IC0yLjIwMjI3LDQuOTE4OTEgLTQuOTE4OTEsNC45MTg5MWgtMTEuOTQ1OTQiLz48L2c+PC9nPjwvZz48L3N2Zz4=';

// CloudDisk block and icon dataURIs
const cd_block_icon = 'data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI2OS43NjY3MSIgaGVpZ2h0PSI1MS41Mzk5NCIgdmlld0JveD0iMCwwLDY5Ljc2NjcxLDUxLjUzOTk0Ij48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMjA1LjExNjY1LC0xNTQuMjMwMDMpIj48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtpc1BhaW50aW5nTGF5ZXImcXVvdDs6dHJ1ZX0iIGZpbGwtcnVsZT0ibm9uemVybyIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLW1pdGVybGltaXQ9IjEwIiBzdHJva2UtZGFzaGFycmF5PSIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBzdHlsZT0ibWl4LWJsZW5kLW1vZGU6IG5vcm1hbCI+PHBhdGggZD0iTTI3Mi44ODMzNiwxODguODA3NTJjMCw4LjI2MzUzIC02LjY5ODkxLDE0Ljk2MjQ0IC0xNC45NjI0NCwxNC45NjI0NGgtMjYuOTMyMzljLTEyLjQ0MzE3LDAuMDA5MjggLTIyLjgxODksLTkuNTE1NDggLTIzLjg3MTg4LC0yMS45MTQwM2MtMS4wNTI5OCwtMTIuMzk4NTUgNy41Njc5MywtMjMuNTM2NjUgMTkuODM0NDUsLTI1LjYyNTljMTIuMjY2NTIsLTIuMDg5MjUgMjQuMDg4NDksNS41NjcgMjcuMTk5MjksMTcuNjE1MDVoMy43NzA1M2M4LjI2MzUzLDAgMTQuOTYyNDQsNi42OTg5MSAxNC45NjI0NCwxNC45NjI0NHoiIGRhdGEtcGFwZXItZGF0YT0ieyZxdW90O29yaWdQb3MmcXVvdDs6bnVsbH0iIGZpbGw9IiMwNTRjNjMiLz48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtvcmlnUG9zJnF1b3Q7Om51bGx9IiBmaWxsPSJub25lIj48cGF0aCBkPSJNMjQ0Ljg3ODg1LDE4MC4yMTc3OGgtMjcuODQ0NTkiLz48cGF0aCBkPSJNMjI0LjMyOTU1LDE2OS4wNzk5NWgxMy4yNTQwM2MxLjA1NjYyLDAuMDAwNTUgMi4wMjE4OSwwLjU5OTE0IDIuNDkyMDksMS41NDUzN2w0LjgwMzE5LDkuNTkyNDZ2OC4zNTMzN2MwLDEuNTM3ODEgLTEuMjQ2NjQsMi43ODQ0NiAtMi43ODQ0NiwyLjc4NDQ2aC0yMi4yNzU2N2MtMS41Mzc4MSwwIC0yLjc4NDQ2LC0xLjI0NjY0IC0yLjc4NDQ2LC0yLjc4NDQ2di04LjM1MzM3bDQuODAzMTksLTkuNTkyNDZjMC40NzAyLC0wLjk0NjI0IDEuNDM1NDcsLTEuNTQ0ODEgMi40OTIxLC0xLjU0NTM3eiIvPjxwYXRoIGQ9Ik0yMjIuNjAzMTksMTg1Ljc4NjdoMC4wMTM5MiIvPjxwYXRoIGQ9Ik0yMjguMTcyMTEsMTg1Ljc4NjdoMC4wMTM5MiIvPjwvZz48L2c+PC9nPjwvc3ZnPg==';
const cd_menu_icon = 'data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI0Ny40OTk3NSIgaGVpZ2h0PSI0Ny40OTk3NSIgdmlld0JveD0iMCwwLDQ3LjQ5OTc1LDQ3LjQ5OTc1Ij48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMjE2LjI1MDEyLC0xNTYuMjUwMTIpIj48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtpc1BhaW50aW5nTGF5ZXImcXVvdDs6dHJ1ZX0iIGZpbGwtcnVsZT0ibm9uemVybyIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2UtbWl0ZXJsaW1pdD0iMTAiIHN0cm9rZS1kYXNoYXJyYXk9IiIgc3Ryb2tlLWRhc2hvZmZzZXQ9IjAiIHN0eWxlPSJtaXgtYmxlbmQtbW9kZTogbm9ybWFsIj48cGF0aCBkPSJNMjE3LjUwMDEzLDE4MGMwLC0xMi40MjYzNCAxMC4wNzM1MywtMjIuNDk5ODggMjIuNDk5ODgsLTIyLjQ5OTg4YzEyLjQyNjM0LDAgMjIuNDk5ODcsMTAuMDczNTMgMjIuNDk5ODcsMjIuNDk5ODhjMCwxMi40MjYzNCAtMTAuMDczNTMsMjIuNDk5ODggLTIyLjQ5OTg3LDIyLjQ5OTg4Yy0xMi40MjYzNCwwIC0yMi40OTk4OCwtMTAuMDczNTMgLTIyLjQ5OTg4LC0yMi40OTk4OHoiIGRhdGEtcGFwZXItZGF0YT0ieyZxdW90O29yaWdQb3MmcXVvdDs6bnVsbH0iIGZpbGw9IiMwNTRjNjMiIHN0cm9rZS13aWR0aD0iMi41IiBzdHJva2UtbGluZWNhcD0iYnV0dCIgc3Ryb2tlLWxpbmVqb2luPSJtaXRlciIvPjxnIGRhdGEtcGFwZXItZGF0YT0ieyZxdW90O29yaWdQb3MmcXVvdDs6bnVsbH0iIGZpbGw9Im5vbmUiIHN0cm9rZS13aWR0aD0iNCIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMjUzLjkyMjI5LDE4MGgtMjcuODQ0NTkiLz48cGF0aCBkPSJNMjMzLjM3Mjk5LDE2OC44NjIxN2gxMy4yNTQwM2MxLjA1NjYyLDAuMDAwNTUgMi4wMjE4OSwwLjU5OTE0IDIuNDkyMDksMS41NDUzN2w0LjgwMzE5LDkuNTkyNDZ2OC4zNTMzN2MwLDEuNTM3ODEgLTEuMjQ2NjQsMi43ODQ0NiAtMi43ODQ0NiwyLjc4NDQ2aC0yMi4yNzU2N2MtMS41Mzc4MSwwIC0yLjc4NDQ2LC0xLjI0NjY0IC0yLjc4NDQ2LC0yLjc4NDQ2di04LjM1MzM3bDQuODAzMTksLTkuNTkyNDZjMC40NzAyLC0wLjk0NjI0IDEuNDM1NDcsLTEuNTQ0ODEgMi40OTIxLC0xLjU0NTM3eiIvPjxwYXRoIGQ9Ik0yMzEuNjQ2NjMsMTg1LjU2ODkyaDAuMDEzOTIiLz48cGF0aCBkPSJNMjM3LjIxNTU1LDE4NS41Njg5MmgwLjAxMzkyIi8+PC9nPjwvZz48L2c+PC9zdmc+';

// Booleans for signifying an update to the global or private data streams, as well as the disk and coin data.
var gotNewGlobalData = false; 
var gotNewPrivateData = false;
var gotNewTrade = false;
var gotDiskData = false;
var gotCoinData = false;
var gotAccountData = false;
var gotNewGlobalLinkedData = false;
var gotNewPrivateLinkedData = false;

// Variables storing global and private stream data transmitted from the server.
var sGData = "";
var sPData = "";
var sGLinkedData = "";
var sPLinkedData = "";

// System variables needed for basic functionality
var sys_status = 0; // System status reporter, 0 = Ready, 1 = Connecting, 2 = Connected, 3 = Disconnected OK, 4 = Disconnected ERR
var userNames = ""; // Usernames list
var uList = "";
var myName = ""; // Username reporter
var servIP = defIP; // Default server IP
var isRunning = false; // Boolean for determining if the connection is alive and well
var wss = null; // Websocket object that enables communications

// Special Features that work when enableSpecialHandshake is set to true (If false, it enables backward-compatibility mode for older application servers)
var linkTo = ''; // Variable for linking to a specific client ID. 
var specialHandshakeAcquired = false; // Determines if new blocks are supported on the server.
var serverVersion = ''; // Diagnostics, gets the server's value for 'vers'.
var globalVars = {}; // Custom globally-readable variables.
var privateVars = {}; // Custom private variables.
var gotNewGlobalVarData = {}; // Booleans for checking if a new value has been written to a global var.
var gotNewPrivateVarData = {}; // Booleans for checking if a new value has been written to a private var.

// Variables for storing CloudAccount data
var isAuth = false;
var accountData = "";
var accMode = "";
var twofactormode = false;

// Variables for storing CloudCoin data
var coinData = '';
var tradeReturn = '';

// Variables for storing CloudDisk data
var diskData = '';
var runningFtp = false;
var ftpData = '';

console.log("[CloudLink Suite] Loading 2/3: Now loading classes...")

// CloudLink class for the primary extension.
class cloudlink {
	constructor(runtime, extensionId) {
		this.runtime = runtime;
	}
	static get STATE_KEY() {
		return 'Scratch.websockets';
	}
	getInfo() {
		return {
			id: 'cloudlink',
			name: 'CloudLink',
			color1: '#054c63',
			color2: '#054c63',
			color3: '#043444',
			blockIconURI: cl_block_icon,
			menuIconURI: cl_menu_icon,
			blocks: [
			{
				opcode: 'returnGlobalData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Global data',
			}, 	{
				opcode: 'returnPrivateData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Private data',
			}, 	{
				opcode: 'returnGlobalLinkedData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Linked Global Data',
			}, 	{
				opcode: 'returnPrivateLinkedData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Linked Private Data',
			}, 	{
				opcode: 'returnLinkData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Link Status',
			}, 	{
				opcode: 'returnUserListData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Usernames',
			}, 	{
				opcode: 'returnUsernameData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'My Username',
			}, 	{
				opcode: 'returnVersionData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Extension Version',
			}, 	{
				opcode: 'returnServerVersion',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Server Version',
			}, 	{
				opcode: 'returnLinkedID',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Linked ID',
			},	{
				opcode: 'returnTestIPData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Test IP',
			}, 	{
				opcode: 'returnVarData',
				blockType: Scratch.BlockType.REPORTER,
				text: '[TYPE] var [VAR] data',
				arguments: {
					VAR: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Apple',
					},
					TYPE: {
						type: Scratch.ArgumentType.STRING,
						menu: 'varmenu',
						defaultValue: 'Global',
					},
				},
			},	{
				opcode: 'parseJSON',
				blockType: Scratch.BlockType.REPORTER,
				text: '[PATH] of [JSON_STRING]',
				arguments: {
					PATH: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'fruit/apples',
					},
					JSON_STRING: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: '{"fruit": {"apples": 2, "bananas": 3}, "total_fruit": 5}',
					},
				},
			}, 	{
				opcode: 'getComState',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Connected?',
			}, 	{
				opcode: 'getUsernameState',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Username synced?',
			}, 	{
				opcode: 'returnIsLinked',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Linked to ID?',
			}, 	{
				opcode: 'returnIsNewData',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Got New [TYPE] Data?',
				arguments: {
					TYPE: {
						type: Scratch.ArgumentType.STRING,
						menu: 'datamenu',
						defaultValue: 'Global',
					},
				},
			}, 	{
				opcode: 'returnIsNewVarData',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Got New [TYPE] Var [VAR] Data?',
				arguments: {
					VAR: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Apple',
					},
					TYPE: {
						type: Scratch.ArgumentType.STRING,
						menu: 'varmenu',
						defaultValue: 'Global',
					},
				},
			}, {
				opcode: 'checkForID',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'ID [ID] Connected?',
				arguments: {
					ID: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Another name',
					},
				},
			}, {
				opcode: 'openSocket',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Connect to [IP]',
				arguments: {
					IP: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: defIP,
					},
				},
			}, 	{
				opcode: 'closeSocket',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Disconnect',
			}, 	{
				opcode: 'setMyName',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Set [NAME] as username',
				arguments: {
					NAME: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'A name',
					},
				},
			},	{
				opcode: 'sendGData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Send [DATA]',
				arguments: {
					DATA: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Apple',
					},
				},
			}, 	{
				opcode: 'sendPData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Send [DATA] to [ID]',
				arguments: {
					DATA: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Apple',
					},
					ID: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'A name',
					},
				},
			},  {
				opcode: 'sendGDataAsVar',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Send Var [VAR] with Data [DATA]',
				arguments: {
					DATA: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Banana',
					},
					VAR: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Apple',
					},
				},
			},	{
				opcode: 'sendPDataAsVar',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Send Var [VAR] to [ID] with Data [DATA]',
				arguments: {
					DATA: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Banana',
					},
					ID: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'A name',
					},
					VAR: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Apple',
					},
				},
			},	{
				opcode: 'refreshUserList',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Refresh User List',
			},	{
				opcode: 'resetNewData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Reset Got New [TYPE] Data',
				arguments: {
					TYPE: {
						type: Scratch.ArgumentType.STRING,
						menu: 'datamenu',
						defaultValue: 'Global',
					},
				},
			},	{
				opcode: 'resetNewVarData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Reset Got New [TYPE] Var [VAR] Data',
				arguments: {
					TYPE: {
						type: Scratch.ArgumentType.STRING,
						menu: 'varmenu',
						defaultValue: 'Global',
					},
					VAR: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Apple',
					},
				},
			},	{
				opcode: 'linkWithID',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Link with ID [ID]',
				arguments: {
					ID: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: '%MS%',
					},
				},
			},	{
				opcode: 'runCMD',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Send CMD [CMD] to ID [ID] with data [DATA]',
				arguments: {
					CMD: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'PING',
					},
					ID: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: '%MS%',
					},
					DATA: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Banana',
					},
				},
			}, 
			],
			menus: {
				coms: {
					items: ["Connected", "Username Synced"]
				},
				datamenu: {
					items: ['Global', 'Private', 'Global (Linked)', 'Private (Linked)'],
				},
				varmenu: {
					items: ['Global', 'Private'],
				},
			}
		};
	}; 
	openSocket(args) {
		servIP = args.IP; // Begin the main updater scripts
		if (!isRunning) {
			sys_status = 1;
			console.log("[CloudLink] Establishing connection...");
			try {
				wss = new WebSocket(servIP);
				wss.onopen = function(e) {
					isRunning = true;
					sys_status = 2; // Connected OK value
					console.log("[CloudLink] Connected.");
					if (enableSpecialHandshake) {
						wss.send("<%sh>\n") // request for special features to be enabled
						console.log("[CloudLink] Attempting special features handshake...")
					}; 
				};
				wss.onmessage = function(event) {
					var rawpacket = String(event.data);
					var obj = JSON.parse(event.data);
					if (obj["type"] == "gs") {
						sGData = String(obj["data"]);
						gotNewGlobalData = true;
					} else if (obj["type"] == "ps") {
						if (String(obj["id"]) == String(myName)) {
						sPData = String(obj["data"]);
						gotNewPrivateData = true;
						};
					} else if (obj["type"] == "dd") {
						if (String(obj["id"]) == String(myName)) {
							diskData = String(obj["data"]);
							gotDiskData = true;
						};
					} else if (obj["type"] == "ftp") {
						if (String(obj["id"]) == String(myName)) {
							if (runningFtp) {
								if (String(obj['data']) != "<TX>") {
									ftpData = String(String(ftpData) + String(obj["data"]));
								} else {
									runningFtp = false;
								};
							};
						};
					} else if (obj["type"] == "ca") {
						if (String(obj["id"]) == String(myName)) {
							if (!twofactormode) {
								if (String(obj["data"]) == "OK") {
									if (accMode == "LI"){
										isAuth = true;
										accMode = "";
										accountData = String(obj["data"]);
										gotAccountData = true;
									} else if (accMode == "LO") {
										isAuth = false;
										accMode = "";
										accountData = String(obj["data"]);
										gotAccountData = true;
									};
								} else {
									if ((accMode == "LI") && !(String(obj["data"]).includes("E:") || String(obj["data"]).includes("I:"))) {
										accMode = "LI_2F"
										twofactormode = true;
									} else {
										accMode = "";
										twofactormode = false;
									};
									accountData = String(obj["data"]);
									gotAccountData = true;
									
								};
							} else {
								if (String(obj["data"]) == "OK") {
									if (accMode == "LI_2F"){
										isAuth = true;
										accMode = "";
										twofactormode = false;
										accountData = String(obj["data"]);
										gotAccountData = true;
									} else if (accMode == "LO") {
										isAuth = false;
										accMode = "";
										twofactormode = false;
										accountData = String(obj["data"]);
										gotAccountData = true;
									}
								} else {
									accountData = String(obj["data"]);
									gotAccountData = true;
								};
							};
						};
					} else if (obj["type"] == "cd") {
						if (String(obj["id"]) == String(myName)) {
							coinData = String(obj["data"]);
							gotCoinData = true;
						};
					} else if (obj["type"] == "ul") {
						userNames = String(obj["data"]);
						userNames = userNames.split(";");
						userNames.pop();
						var uListTemp = "";
						var i;
						for (i = 0; i < userNames.length; i++) {
							if (!userNames[i].includes("%")) {
								uListTemp = (String(uListTemp) + String(userNames[i])+ "; ");
							};
						};
						uList = uListTemp;
					} else if (obj["type"] == "ru") {
						if (myName != "") {
							wss.send("<%sn>\n" + myName);
						};
					} else if (obj["type"] == "direct") {
						var ddata = obj['data'];
						if (ddata['type'] == "vers") {
							specialHandshakeAcquired = true;
							console.log("[CloudLink] Special features handshake acknowledged!")
							serverVersion = ddata["data"];
							console.log("[CloudLink] Server version: " + String(serverVersion));
						};
					} else if (obj["type"] == "sf") {
						try {
							var ddata = obj['data'];
							if (ddata['type'] == "gs") {
								sGData = String(ddata['data']);
								gotNewGlobalData = true;
							} else if (ddata['type'] == "lm") {
								if (ddata['mode'] == "g") {
									sGLinkedData = String(ddata['data']);
									gotNewGlobalLinkedData = true;
								} else if (ddata['mode'] == "p") {
									sPLinkedData = String(ddata['data']);
									gotNewPrivateLinkedData = true;
								}
							} else if (ddata['type'] == "vm") {
								if (ddata['mode'] == "g") {
									globalVars[ddata['var']] = ddata['data'];
									gotNewGlobalVarData[ddata['var']] = true;
								} else if (ddata['mode'] == "p") {
									privateVars[ddata['var']] = ddata['data'];
									gotNewPrivateVarData[ddata['var']] = true;
								}
							} else if (ddata['type'] == "ps") {
								sPData = String(ddata['data']);
								gotNewPrivateData = true;
							}
						} catch(err) {
							console.log("[CloudLink] Oops! An error occured. "+String(err));
						}
					} else {
						console.log("[CloudLink] Error! Unknown packet data: " + String(rawpacket));
					};
				};
				wss.onclose = function(event) {
					isRunning = false;
					myName = "";
					gotNewGlobalData = false;
					gotNewPrivateData = false;
					gotNewGlobalLinkedData = false;
					gotNewPrivateLinkedData = false;
					gotNewTrade = false;
					gotDiskData = false;
					gotCoinData = false;
					gotAccountData = false;
					userNames = "";
					sGData = "";
					sPData = "";
					sGLinkedData = "";
					sPLinkedData = "";
					coinData = "";
					tradeReturn = "";
					diskData = "";
					accountData = "";
					accMode = "";
					isAuth = false;
					sys_status = 3; // Disconnected OK value
					runningFtp = false;
					ftpData = '';
					serverVersion = '';
					linkTo = '';
					globalVars = {};
					privateVars = {};
					specialHandshakeAcquired = false;
					gotNewGlobalVarData = {};
					gotNewPrivateVarData = {};
					uList = "";
					wss = null;
					if (event.wasClean) {
						sys_status = 3; // Disconnected OK value
						console.log("[CloudLink] Disconnected: Safely disconnected.");
					} else {
						sys_status = 4; // Connection lost value
						console.log("[CloudLink] Disconnected: Lost connection.");
					};
				};
			} catch(err) {
				throw(err)
			};
		} else {
			return "Connection already established.";
		};
	}; // end the updater scripts
	closeSocket() {
		if (isRunning) {
			wss.send("<%ds>\n" + myName); // send disconnect command in header before shutting down link
			wss.close(1000);
			isRunning = false;
			myName = "";
			gotNewGlobalData = false;
			gotNewPrivateData = false;
			gotNewGlobalLinkedData = false;
			gotNewPrivateLinkedData = false;
			gotNewTrade = false;
			gotDiskData = false;
			gotCoinData = false;
			gotAccountData = false;
			userNames = "";
			sGData = "";
			sPData = "";
			sGLinkedData = "";
			sPLinkedData = "";
			coinData = "";
			tradeReturn = "";
			diskData = "";
			accountData = "";
			accMode = "";
			isAuth = false;
			sys_status = 3; // Disconnected OK value
			runningFtp = false;
			ftpData = '';
			serverVersion = '';
			linkTo = '';
			globalVars = {};
			privateVars = {};
			specialHandshakeAcquired = false;
			gotNewGlobalVarData = {};
			gotNewPrivateVarData = {};
			uList = "";
			wss = null;
			return ("Connection closed.");
		} else {
			return ("Connection already closed.");
		};
	};
	getComState() {
		return isRunning;
	};
	checkForID(args) {
		if (isRunning) {
			return (userNames.indexOf(String(args.ID)) >= 0);
		} else {
			return false;
		};
	};
	getUsernameState() {
		if (isRunning) {
			if (myName != '') {
				return (userNames.indexOf(String(myName)) >= 0);
			} else {
				return false;
			}
		} else {
			return false;
		};
	};
	sendGData(args) {
		if (isRunning) {
			if (linkTo == "") {
				wss.send("<%gs>\n" + myName + "\n" + args.DATA);
			} else {
				wss.send("<%l_g>\n0\n" + myName + "\n" + args.DATA);
			};
			return "Sent data successfully.";
		} else {
			return "Connection closed, no action taken.";
		}
	};
	sendPData(args) {
		if (isRunning) {
			if (myName != "") {
				if (args.ID != myName) {
					if (linkTo == "") {
						wss.send("<%ps>\n" + myName + "\n" + args.ID + "\n" + args.DATA);
					} else {
						wss.send("<%l_p>\n0\n" + myName + "\n" + args.ID + "\n" + args.DATA);
					};
					return "Sent data successfully.";
				} else {
					return "Can't send data to yourself!";
				};
			} else {
				return "Username not set, no action taken.";
			}
		} else {
			return "Connection closed, no action taken.";
		};
	}; 
	sendGDataAsVar(args) {
		if (isRunning && specialHandshakeAcquired) {
			if (linkTo != "") {
				wss.send("<%l_g>\n2\n" + myName + "\n" + args.VAR + "\n" + args.DATA);
			} else {
				wss.send("<%l_g>\n1\n" + myName + "\n" + args.VAR + "\n" + args.DATA);
			}
			return "Sent data successfully.";
		} else {
			if (isRunning) {
				return "Server is out-of-date / Doesn't support special features!";
			} else {
				return "Connection closed, no action taken.";
			}
		}
	};
	sendPDataAsVar(args) {
		if (isRunning && specialHandshakeAcquired) {
			if (myName != "") {
				if (args.ID != myName) {
					if (linkTo != "") {
						wss.send("<%l_p>\n2\n" + myName + "\n" + args.ID + "\n" + args.VAR + "\n" + args.DATA);
					} else {
						wss.send("<%l_p>\n1\n" + myName + "\n" + args.ID + "\n" + args.VAR + "\n" + args.DATA);
					}
					return "Sent data successfully.";
				} else {
					return "Can't send data to yourself!";
				}
			} else {
				return "Username not set, no action taken.";
			}
		} else {
			if (isRunning) {
				return "Server is out-of-date / Doesn't support special features!";
			} else {
				return "Connection closed, no action taken.";
			}
		};
	};
	runCMD(args) {
		if (isRunning) {
			if (myName != "") {
				if (args.ID != myName) {
					wss.send("<%ps>\n" + myName + "\n" + args.ID + '\n{"cmd":"' + args.CMD + '","id":"' + myName + '","data":"' + args.DATA + '"}');
					return "Sent data successfully.";
				} else {
					return "Can't send data to yourself!";
				};
			} else {
				return "Username not set, no action taken.";
			}
		} else {
			return "Connection closed, no action taken.";
		};
	};
	returnGlobalData() {
		return sGData;
	};
	returnPrivateData() {
		return sPData;
	};
	returnGlobalLinkedData() {
		return sGLinkedData;
	};
	returnPrivateLinkedData() {
		return sPLinkedData;
	};
	returnVarData(args) {
		if (args.TYPE == "Global") {
			if (args.VAR in globalVars) {
				return globalVars[args.VAR];
			} else {
				return "";
			}
		} else if (args.TYPE == "Private") {
			if (args.VAR in privateVars) {
				return privateVars[args.VAR];
			} else {
				return "";
			}
		}
	};
	returnIsNewVarData(args) {
		if (args.TYPE == "Global") {
			if (args.VAR in globalVars) {
				return gotNewGlobalVarData[args.VAR];
			} else {
				return false;
			}
		} else if (args.TYPE == "Private") {
			if (args.VAR in privateVars) {
				return gotNewPrivateVarData[args.VAR];
			} else {
				return false;
			}
		};
	};
	returnLinkData() {
		return sys_status;
	}; 
	returnUserListData() {
		return uList;
	}; 
	returnUsernameData() {
		return myName;
	}; 
	returnVersionData() {
		return vers;
	}; 
	returnTestIPData() {
		return testIP;
	};
	returnServerVersion() {
		return serverVersion;
	};
	returnIsNewData(args) {
		if (args.TYPE == "Global") {
			return gotNewGlobalData;
		};
		if (args.TYPE == "Private") {
			return gotNewPrivateData;
		};
		if (args.TYPE == "Global (Linked)") {
			return gotNewGlobalLinkedData;
		};
		if (args.TYPE == "Private (Linked)") {
			return gotNewPrivateLinkedData;
		};
	}
	setMyName(args) {
		if (myName == "") {
			if (isRunning) {
				if (args.NAME != "") {
					if (!(userNames.indexOf(args.NAME) >= 0)) {
						if (args.NAME.length > 20) {
							return "Your username must be 20 characters or less!"
						} else {
							if (args.NAME.length != 0) {
								if (args.NAME == "%CA%" || args.NAME == "%CC%" || args.NAME == "%CD%" || args.NAME == "%MS%"){
								return "That ID is reserved.";
								} else {
									wss.send("<%sn>\n" + args.NAME); // begin packet data with setname command in the header
									myName = args.NAME;
									return "Set username on server successfully.";
								}
							} else {
								return "You can't have a blank username!";
							}
						}
					} else {
						return "You can't have the same name as someone else!";
					}
				} else {
					return "You cannot have a blank username!";
				}
			} else {
				return "Connection closed, no action taken.";
			}
		} else {
			return "Username already set!";
		};
	};
	parseJSON({
		PATH,
		JSON_STRING
	}) {
		try {
			const path = PATH.toString().split('/').map(prop => decodeURIComponent(prop));
			if (path[0] === '') path.splice(0, 1);
			if (path[path.length - 1] === '') path.splice(-1, 1);
			let json;
			try {
				json = JSON.parse(' ' + JSON_STRING);
			} catch (e) {
				return e.message;
			}
			path.forEach(prop => json = json[prop]);
			if (json === null) return 'null';
			else if (json === undefined) return '';
			else if (typeof json === 'object') return JSON.stringify(json);
			else return json.toString();
		} catch (err) {
			return '';
		}
	};
	refreshUserList() {
		if (isRunning == true) {
			wss.send("<%rf>\n"); // begin packet data with global stream idenifier in the header
			return "Sent request successfully.";
		} else {
			return "Connection closed, no action taken.";
		}
	};
	resetNewData(args) {
		if (args.TYPE == "Global") {
			if (gotNewGlobalData == true) {
				gotNewGlobalData = false;
			};
		};
		if (args.TYPE == "Private") {
			if (gotNewPrivateData == true) {
				gotNewPrivateData = false;
			};
		};
		if (args.TYPE == "Global (Linked)") {
			if (gotNewGlobalLinkedData == true) {
				gotNewGlobalLinkedData = false;
			};
		};
		if (args.TYPE == "Private (Linked)") {
			if (gotNewPrivateLinkedData == true) {
				gotNewPrivateLinkedData = false;
			};
		};
	};
	resetNewVarData(args) {
		if (args.TYPE == "Global") {
			if (args.VAR in globalVars) {
				gotNewGlobalVarData[args.VAR] = false;
			}
		} else if (args.TYPE == "Private") {
			if (args.VAR in privateVars) {
				gotNewPrivateVarData[args.VAR] = false;
			}
		}
	};
	linkWithID(args) {
		if (isRunning && specialHandshakeAcquired) {
			if (myName != "") {
				if (args.ID == "") {
					if (linkTo != "") {
						linkTo = "";
						sGLinkedData = "";
						sPLinkedData = "";
						gotNewGlobalLinkedData = false;
						gotNewPrivateLinkedData = false;
						globalVars = {};
						privateVars = {};
						gotNewGlobalVarData = {};
						gotNewPrivateVarData = {};
						wss.send("<%rt>\n" + myName);
						return "Now linked to main link.";
					} else {
						return "Already linked to main link!";
					}
				} else {
					if (userNames.indexOf(args.ID) >= 0) {
						if (myName != args.ID) {
							if (linkTo != args.ID) {
								linkTo = args.ID;
								sGLinkedData = "";
								sPLinkedData = "";
								gotNewGlobalLinkedData = false;
								gotNewPrivateLinkedData = false;
								globalVars = {};
								privateVars = {};
								gotNewGlobalVarData = {};
								gotNewPrivateVarData = {};
								wss.send("<%rl>\n" + myName + "\n" + args.ID);
								return ("Now linked to ID: "+String(args.ID)+".");
							} else {
								return ("Already linked to ID: "+String(args.ID)+"!");
							}
						} else {
							return "Can't link to yourself!";
						}
					} else {
						return "ID does not exist!";
					}
				}
			} else {
				return "Username not set! No action taken.";
			}
		} else {
			if (isRunning) {
				return "Server is out-of-date / Doesn't support special features!";
			} else {
				return "Connection closed, no action taken.";
			}
		};
	};
	returnIsLinked() {
		return ((linkTo != "") && specialHandshakeAcquired);
	};
	returnLinkedID() {
		return linkTo;
	};
};

// CloudAccount class for enabling access to the Disk and Coin APIs.
class cloudaccount {
	constructor(runtime, extensionId) {
		this.runtime = runtime;
	}
	static get STATE_KEY() {
		return 'Scratch.websockets';
	}
	getInfo() {
		return {
			id: 'cloudaccount',
			name: 'CloudAccount',
			color1: '#054c63',
			color2: '#054c63',
			color3: '#043444',
			blockIconURI: ca_block_icon,
			menuIconURI: ca_menu_icon,
			blocks: [
			{
				opcode: 'reportData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Account data',
			}, {
				opcode: 'getComState',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Connected?',
			}, {
				opcode: 'gotData',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Got new Account data?',
			}, {
				opcode: 'returnAuth',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Logged in?',
			}, {
				opcode: 'resetNewData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Reset Got New Account Data',
			}, {
				opcode: 'doAcc',
				blockType: Scratch.BlockType.COMMAND,
				text: '[ACCMODE] with password [pswd]',
				arguments: {
					ACCMODE: {
						type: Scratch.ArgumentType.STRING,
						menu: 'accmenu',
						defaultValue: 'Login',
					},
					pswd: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: ' ',
					},
				},
			}, {
				opcode: 'loginTwoFactor',

				blockType: Scratch.BlockType.COMMAND,
				text: 'Login with 2-Factor Authentication',
			}, {
				opcode: 'toggleTwoFactor',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Toggle 2-Factor Authentication',
			}, {
				opcode: 'checkAcc',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Check account',
			}, {
				opcode: 'logoutAcc',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Logout',
			}, 
			],
			menus: {
				accmenu: {
					items: ['Login', 'Register / Change Password', 'Delete Account'],
				},
				accmenu_2F: {
					items: ['Login', 'Register', 'Delete Account'],
				},
			},
		};
	};
	reportData() {
		return accountData;
	};
	gotData() {
		return gotAccountData;
	};
	getComState() {
		if (isRunning) {
			if (userNames.indexOf("%CA%") >= 0) {
				return true;
			} else {
				return false;
			}
		} else {
			return false;
		}
	};
	returnAuth() {
		return isAuth;
	};
	resetNewData() {
		if (gotAccountData) {
			gotAccountData = false;
		}
	};
	doAcc(args) {
		if (args.ACCMODE == "Login") { 
			if (isRunning) {
				if (!isAuth) {
					if (myName != ""){
						if (userNames.indexOf('%CA%') >= 0) {
							if (!((args.pswd).length < 6)) {
								accMode = "LI"
								twofactormode = false
								wss.send("<%ps>\n" + myName + '\n%CA%\n{"cmd":"LOGIN","id":"'+ myName+'", "data":"'+args.pswd+'"}\n');
								return "Sent request successfully.";
							} else {
								return "Password cannot be shorter than 6 characters!";
							}
						} else {
							return "CloudAccount API not connected! Try again later.";
						}
					} else {
						return "Username not set! No action taken.";
					}
				} else {
					return "Already logged in!";
				};
			} else {
				return "Connection closed, no action taken.";
			};
		};
		if (args.ACCMODE == "Register / Change Password") {
			if (isRunning) {
				if (myName != ""){
					if (userNames.indexOf('%CA%') >= 0) {
						if (!((args.pswd).length < 6)) {
							accMode = "LI"
							twofactormode = false
							wss.send("<%ps>\n" + myName + '\n%CA%\n{"cmd":"REGISTER","id":"'+ myName+'", "data":"'+args.pswd+'"}\n');
							return "Sent request successfully.";
						} else {
							return "Password cannot be shorter than 6 characters!";
						}
					} else {
						return "CloudAccount API not connected! Try again later.";
					}
				} else {
					return "Username not set! No action taken.";
				}
			} else {
				return "Connection closed, no action taken.";
			};
		};
		if (args.ACCMODE == "Delete Account") {
			if (isRunning) {
				if (myName != ""){
					if (userNames.indexOf('%CA%') >= 0) {
						accMode = "LO"
						twofactormode = false
						wss.send("<%ps>\n" + myName + '\n%CA%\n{"cmd":"DELETE","id":"'+ myName+'", "data":"'+args.pswd+'"}\n');
						return "Sent request successfully.";
					} else {
						return "CloudAccount API not connected! Try again later.";
					}
				} else {
					return "Username not set! No action taken.";
				}
			} else {
				return "Connection closed, no action taken.";
			};
		};
	};
	toggleTwoFactor() {
		if (isRunning) {
				if (myName != ""){
					if (userNames.indexOf('%CA%') >= 0) {
						accMode = "LI_2F"
						twofactormode = false
						wss.send("<%ps>\n" + myName + '\n%CA%\n{"cmd":"REGISTER_2F","id":"'+ myName+'", "data":""}\n');
						return "Sent request successfully.";
					} else {
						return "CloudAccount API not connected! Try again later.";
					}
				} else {
					return "Username not set! No action taken.";
				}
			} else {
				return "Connection closed, no action taken.";
		}
	};
	loginTwoFactor() {
		if (isRunning) {
			if (!isAuth) {
				if (myName != ""){
					if (userNames.indexOf('%CA%') >= 0) {
						accMode = "LI_2F"
						twofactormode = true
						wss.send("<%ps>\n" + myName + '\n%CA%\n{"cmd":"LOGIN_2F","id":"'+ myName+'", "data":""}\n');
						return "Sent request successfully.";
					} else {
						return "CloudAccount API not connected! Try again later.";
					}
				} else {
					return "Username not set! No action taken.";
				}
			} else {
				return "Already logged in!";
			}
		} else {
			return "Connection closed, no action taken.";
	    }
    };
	logoutAcc() {
		if (isRunning) {
			if (myName != "") {
				if (isAuth) {
					if (userNames.indexOf('%CA%') >= 0) {
						accMode = "LO";
						wss.send("<%ps>\n" + myName + '\n%CA%\n{"cmd":"LOGOUT","id":"'+ myName+'", "data":""}\n');
						return "Sent request successfully.";
					} else {
						return "CloudAccount API not connected! Try again later.";
					}
				} else {
					return "Already logged out!";
				}
			} else {
				return "Username not set! No action taken.";
			};
		} else {
			return "Connection closed, no action taken.";
		};
	};
	checkAcc() {
		if (isRunning) {
				if (myName != "") {
					if (userNames.indexOf('%CA%') >= 0) {
						gotAccountData = false;
						wss.send("<%ps>\n" + myName + '\n%CA%\n{"cmd":"CHECK","id":"'+ myName+'", "data":""}\n');
						return "Sent request successfully.";
					} else {
						return "CloudAccount API not connected! Try again later.";
					}
				} else {
					return "Username not set! No action taken.";
				}
			} else {
				return "Connection closed, no action taken.";
		};
	};
};

// CloudCoin class for accessing the CloudCoin API.
class cloudcoin {
	constructor(runtime, extensionId) {
		this.runtime = runtime;
	}
	static get STATE_KEY() {
		return 'Scratch.websockets';
	}
	getInfo() {
		return {
			id: 'cloudcoin',
			name: 'CloudCoin',
			color1: '#054c63',
			color2: '#054c63',
			color3: '#043444',
			blockIconURI: cc_block_icon,
			menuIconURI: cc_menu_icon,
			blocks: [
			{
				opcode: 'reportData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Coin data',
			}, {
				opcode: 'getComState',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Connected?',
			}, {
				opcode: 'gotData',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Got new Coin data?',
			}, {
				opcode: 'resetNewData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Reset Got New Coin Data',
			}, {
				opcode: 'checkBal',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Check Balance',
			}, {
				opcode: 'setCoins',
				blockType: Scratch.BlockType.COMMAND,
				text: '[coinmode] [coins] coins',
				arguments: {
					coins: {
						type: Scratch.ArgumentType.NUMBER,
						defaultValue: '50',
					},
					coinmode: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Spend',
						menu: 'coinmenu',
					},
				},
			}, {
				opcode: 'tradeCoins',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Trade [coins] coins with [user]',
				arguments: {
					coins: {
						type: Scratch.ArgumentType.NUMBER,
						defaultValue: '50',
					},
					user: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'A name',
					},
				},
			},
			],
			menus: {
				coinmenu: {
					items: ['Spend', 'Earn'],
				},
				coinreporter: {
					items: ['Spend', 'Earn', 'Trade'],
				},
			},
		};
	};
	reportData() {
		return coinData;
	};
	getComState() {
		if (isRunning) {
			if (userNames.indexOf("%CC%") >= 0) {
				return true;
			} else {
				return false;
			}
		} else {
			return false;
		}
	};
	gotData() {
		return gotCoinData;
	};
	resetNewData() {
		if (gotCoinData) {
			gotCoinData = false;
		}
	};
	checkBal() {
		if (myName != "") {
			if (userNames.indexOf('%CC%') >= 0) {
				if (isAuth) {
					wss.send("<%ps>\n" + myName + '\n%CC%\n{"cmd":"CHECK","id":"'+ myName+'", "data":""}\n');
					return "Sent request successfully.";
				} else {
						return "Not logged in!";
				}
			} else {
				return "CloudCoin API not connected! Try again later.";
			}
		} else {
			return "Username not set, no action taken.";
		};
	};
	setCoins(args) {
		if (isRunning) {
			if (args.coinmode == "Spend") {
				if (myName != "") {
					if (userNames.indexOf('%CC%') >= 0) {
						if (isAuth) {
							wss.send("<%ps>\n" + myName + '\n%CC%\n{"cmd":"SPEND","id":"'+ myName+'", "data":"' + String(args.coins) + '"}\n');
							return "Sent request successfully.";
						} else {
							return "Not logged in!";
						}
					} else {
						return "CloudCoin API not connected! Try again later.";
					}
				} else {
					return "Username not set, no action taken.";
				}
			}
			if (args.coinmode == "Earn") {
				if (myName != "") {
					if (userNames.indexOf('%CC%') >= 0) {
						if (isAuth) {
							wss.send("<%ps>\n" + myName + '\n%CC%\n{"cmd":"EARN","id":"'+ myName+'", "data":"' + String(args.coins) + '"}\n');
							return "Sent request successfully.";
						} else {
							return "Not logged in!";
						}
					} else {
						return "CloudCoin API not connected! Try again later.";
					}
				} else {
					return "Username not set, no action taken.";
				}
			}
		} else {
			return "Connection closed, no action taken."
		};
	};
	tradeCoins(args) {
		return "This block doesn't work yet. Sorry!"
	};
};

// CloudDisk class for accessing the CloudDisk API.
class clouddisk {
	constructor(runtime, extensionId) {
		this.runtime = runtime;
	}
	static get STATE_KEY() {
		return 'Scratch.websockets';
	}
	getInfo() {
		return {
			id: 'clouddisk',
			name: 'CloudDisk',
			color1: '#054c63',
			color2: '#054c63',
			color3: '#043444',
			blockIconURI: cd_block_icon,
			menuIconURI: cd_menu_icon,
			blocks: [
			{
				opcode: 'reportDiskData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Disk data',
			}, {
				opcode: 'reportFTPData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'FTP data',
			}, {
				opcode: 'getComState',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Connected?',
			}, {
				opcode: 'gotData',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Got new Disk data?',
			}, {
				opcode: 'resetNewData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Reset Got New Disk Data',
			}, {
				opcode: 'readData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Read data on slot [slot]',
				arguments: {
					slot: {
						type: Scratch.ArgumentType.NUMBER,
						menu: 'diskSlot',
					},
				},
			}, {
				opcode: 'writeData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Write data [data] to slot [slot]',
				arguments: {
					data: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'abc123',
					},
					slot: {
						type: Scratch.ArgumentType.NUMBER,
						menu: 'diskSlot',
					},
				},
			}, {
				opcode: 'getFTPFileList',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Get a List of Files for FTP',
			}, {
				opcode: 'getFTPFileInfo',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Get file [fname] info for FTP',
				arguments: {
					fname: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'sample.txt',
					},
				},
			}, {
				opcode: 'initFTP_DL',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Download file [fname] from FTP',
				arguments: {
					fname: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'sample.txt',
					},
				},
			}, {
				opcode: 'initFTP_UL',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Upload file [fname] to FTP with data [fdata]',
				arguments: {
					fname: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'sample.txt',
					},
					fdata: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Hello, World!',
					},
				},
			}, {
				opcode: 'abortFTP',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Abort FTP'
			},
			],
			menus: {
				diskSlot: {
					acceptReporters: true,
					items: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
				},
			},
		};
	};
	reportDiskData() {
		return diskData;
	};
	reportFTPData() {
		return ftpData;
	};
	getComState() {
		if (isRunning) {
			if (userNames.indexOf("%CD%") >= 0) {
				return true;
			} else {
				return false;
			}
		} else {
			return false;
		}
	};
	resetNewData(args) {
		gotDiskData = false;
	};
	gotData(args) {
		return gotDiskData;
	};
	getFTPFileList(){
		if (isRunning) {
			if (isAuth) {
				wss.send("<%ftp>\n" + myName + '\n%CD%\n{"cmd":"GETLIST","id":"'+ myName+'", "data":""}\n');
				return "Sent request successfully.";
			} else {
				return "Not Logged In!";
			};
		} else {
			return "Connection closed, no action taken.";
		};
	};
	getFTPFileInfo(args){
		if (isRunning) {
			if (isAuth) {
				wss.send("<%ftp>\n" + myName + '\n%CD%\n{"cmd":"GETINFO","id":"'+ myName+'", "data":"'+args.fname+'"}\n');
				return "Sent request successfully.";
			} else {
				return "Not Logged In!";
			};
		} else {
			return "Connection closed, no action taken.";
		};
	};
	initFTP_DL(args){
		if (isRunning) {
			if (isAuth) {
				if (!runningFtp){
					ftpData = '';
					wss.send("<%ftp>\n" + myName + '\n%CD%\n{"cmd":"GET","id":"'+ myName+'", "data":"'+args.fname+'"}\n');
					runningFtp = true;
					return "File downloading...";
				} else {
					return "Already running FTP!";
				}
			} else {
				return "Not Logged In!";
			};
		} else {
			return "Connection closed, no action taken.";
		};
	};
	initFTP_UL(args){
		if (isRunning) {
			if (isAuth) {
				if (!runningFtp){
					wss.send("<%ftp>\n" + myName + '\n%CD%\n{"cmd":"PUT","id":"'+ myName+'", "data":{"fname":"'+args.fname+'", "fdata":"'+args.fdata+'"}}\n');
					runningFtp = true;
					return "File uploading...";
				} else {
					return "Already running FTP!";
				}
			} else {
				return "Not Logged In!";
			};
		} else {
			return "Connection closed, no action taken.";
		};
	};
	abortFTP(){
		if (isRunning) {
			if (isAuth) {
				if (runningFtp){
					wss.send("<%ftp>\n" + myName + '\n%CD%\n{"cmd":"ABORT","id":"'+ myName+'", "data":""}\n');
					runningFtp = false;
					ftpData = '';
					return "Sent request successfully.";
				} else {
					return "Stopped FTP!"
				}
			} else {
				return "Not Logged In!";
			};
		} else {
			return "Connection closed, no action taken.";
		};
	};
	readData(args) {
		if (isRunning) {
			if (myName != "") {
				if (userNames.indexOf('%CD%') >= 0) {
					if (isAuth) {
						wss.send("<%ps>\n" + myName + '\n%CD%\n{"cmd":"READ","id":"'+ myName+'", "data":"' + args.slot + '"}\n');
						return "Sent request successfully.";
					} else {
						return "Not logged in!";
					}
				}
				else {
					return "CloudDisk API not connected! Try again later.";
				}
			} else {
				return "Username not set, no action taken.";
			}
		} else {
			return "Connection closed, no action taken.";
		};
	};
	writeData(args) {
		if (isRunning) {
			if (myName != "") {
				if (userNames.indexOf('%CD%') >= 0) {
					if (isAuth) {
						wss.send("<%ps>\n" + myName + '\n%CD%\n{"cmd":"WRITE","id":"'+ myName+'", "data":{"slot":"' + args.slot + '", "data":"'+args.data+'"}}\n');
						return "Sent request successfully.";
					} else {
						return "Not logged in!";
					}
				}
				else {
					return "CloudDisk API not connected! Try again later.";
				}
			} else {
				return "Username not set, no action taken.";
			}
		} else {
			return "Connection closed, no action taken.";
		};
	};
};

console.log("[CloudLink Suite] Loading 3/3: Finishing load: Adding to ScratchBlocks...");
Scratch.extensions.register(new cloudlink());
Scratch.extensions.register(new cloudaccount());
Scratch.extensions.register(new cloudcoin());
Scratch.extensions.register(new clouddisk());
console.log("[CloudLink Suite] Loaded MikeDEV's CloudLink Suite successfully. You are running version "+ vers +". WARNING! YOU ARE USING A BETA RELEASE OF THE SUITE. If you find any bugs, please report them in https://www.github.com/MikeDev101/cloudlink/issues");
