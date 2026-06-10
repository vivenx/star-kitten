from views.effects.attack_effects import EnergyWaveEffect, SlashEffect


class CombatEffectsView:
    def __init__(self):
        self.slash_effects = []
        self.energy_wave_phases = {}

    def update(self, dt, combat_system):
        for event in combat_system.consume_attack_visual_events():
            if event["type"] == "slash":
                self.slash_effects.append(
                    SlashEffect(event["rect"], event["direction"], event["color"])
                )

        for effect in self.slash_effects:
            effect.update(dt)
        self.slash_effects = [effect for effect in self.slash_effects if effect.is_alive()]

        alive_wave_ids = {id(wave) for wave in combat_system.energy_waves}
        self.energy_wave_phases = {
            wave_id: phase
            for wave_id, phase in self.energy_wave_phases.items()
            if wave_id in alive_wave_ids
        }
        for wave in combat_system.energy_waves:
            self.energy_wave_phases[id(wave)] = self.energy_wave_phases.get(id(wave), 0.0) + dt * 12

    def draw(self, surface, combat_system):
        for effect in self.slash_effects:
            effect.draw(surface)

        for wave in combat_system.energy_waves:
            EnergyWaveEffect.draw_wave(surface, wave, self.energy_wave_phases.get(id(wave), 0.0))
