import asyncio
from src.bcch_client import BCChClient

async def test():
    client = BCChClient()
    data = await client.get_series("F032.IMC.IND.Z.Z.EP18.Z.Z.0.M", "2026-01-01", "2026-07-01")
    obs = data.get("Series", {}).get("Obs", [])
    print(f"Imacec Empalmado (F032.IMC.IND.Z.Z.EP18.Z.Z.0.M): {len(obs)} datos. Ultimo: {obs[-1]}")

if __name__ == "__main__":
    asyncio.run(test())
