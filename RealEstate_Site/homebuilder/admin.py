from django.contrib import admin
from django.utils.html import format_html
from .models import HomeLayout, Room

class RoomInline(admin.TabularInline):
    model = Room
    extra = 0
    fields = ('room_type', 'floor', 'x', 'y', 'width', 'height')
    readonly_fields = ('room_type', 'floor', 'x', 'y', 'width', 'height')
    can_delete = True
    show_change_link = True
    ordering = ('floor', 'room_type')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(HomeLayout)
class HomeLayoutAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'floors',
        'length',
        'width',
        'total_rooms',
        'created_at_formatted'
    )
    list_filter = (
        'floors',
        'created_at',
        ('user', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
    )
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'floors', 'created_at'),
            'classes': ('wide',),
        }),
        ('Dimensions', {
            'fields': ('length', 'width'),
            'classes': ('wide',),
        }),
        ('Request Payload', {
            'fields': ('request_payload',),
            'classes': ('wide', 'collapse'),
        }),
        ('Layout Summary', {
            'fields': ('room_summary',),
            'classes': ('wide',),
        }),
    )

    readonly_fields = ('created_at', 'room_summary')
    inlines = [RoomInline]

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_formatted.short_description = 'Created'
    created_at_formatted.admin_order_field = 'created_at'

    def total_rooms(self, obj):
        return obj.rooms.count()
    total_rooms.short_description = 'Total Rooms'
    total_rooms.admin_order_field = 'rooms__count'

    def room_summary(self, obj):
        rooms = obj.rooms.all()
        if not rooms:
            return "No rooms defined"

        room_counts = {}
        for room in rooms:
            room_type = room.get_room_type_display()
            room_counts[room_type] = room_counts.get(room_type, 0) + 1

        summary_parts = []
        for room_type, count in sorted(room_counts.items()):
            summary_parts.append(f"{room_type}: {count}")

        return format_html('<br>'.join(summary_parts))
    room_summary.short_description = 'Room Distribution'

    actions = ['duplicate_layout']

    def duplicate_layout(self, request, queryset):
        for layout in queryset:
            new_layout = HomeLayout.objects.create(
                user=layout.user,
                length=layout.length,
                width=layout.width,
                floors=layout.floors
            )

            for room in layout.rooms.all():
                Room.objects.create(
                    home=new_layout,
                    room_type=room.room_type,
                    floor=room.floor,
                    x=room.x,
                    y=room.y,
                    width=room.width,
                    height=room.height
                )

        self.message_user(request, f"Successfully duplicated {queryset.count()} layout(s).")
    duplicate_layout.short_description = "Duplicate selected layouts"

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'room_type',
        'home',
        'floor',
        'dimensions',
        'position',
    )
    list_filter = (
        'room_type',
        'floor',
        ('home', admin.RelatedOnlyFieldListFilter),
        ('home__user', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        'home__user__username',
        'home__user__email',
        'room_type',
    )
    ordering = ('home', 'floor', 'room_type')

    fieldsets = (
        ('Basic Information', {
            'fields': ('home', 'room_type', 'floor'),
            'classes': ('wide',),
        }),
        ('Position & Dimensions', {
            'fields': ('x', 'y', 'width', 'height'),
            'classes': ('wide',),
        }),
    )

    def dimensions(self, obj):
        return f"{obj.width:.1f} × {obj.height:.1f}"
    dimensions.short_description = 'Size (W×H)'
    dimensions.admin_order_field = 'width'

    def position(self, obj):
        return f"({obj.x:.1f}, {obj.y:.1f})"
    position.short_description = 'Position (X,Y)'
    position.admin_order_field = 'x'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('home', 'home__user')