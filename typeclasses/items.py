from evennia import DefaultObject

class Item(DefaultObject):
    def access(
        self, accessing_obj, access_type="read", default=False, no_superuser_bypass=False, **kwargs
    ):
        if access_type == "describe":
            return not self.db.desc
        if access_type == "taste":
            return not self.db.taste

        result = super().access(
            accessing_obj,
            access_type=access_type,
            default=default,
            no_superuser_bypass=no_superuser_bypass,
        )

        return result
