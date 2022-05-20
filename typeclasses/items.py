from evennia import DefaultObject

class Item(DefaultObject):
    def access(
        self, accessing_obj, access_type="read", default=False, no_superuser_bypass=False, **kwargs
    ):
        if access_type in ['desribe', 'taste', 'touch', 'smell']:
            return not self.attributes.has(access_type)

        result = super().access(
            accessing_obj,
            access_type=access_type,
            default=default,
            no_superuser_bypass=no_superuser_bypass,
        )

        return result
