EventScript_JohtoPkmnCenterNurse::
	lock
	faceplayer
	call EventScript_PkmnCenterNurse_Frlg
	release
	end

EventScript_JohtoMartClerk::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart JohtoMart_Items
	msgbox gText_PleaseComeAgain
	release
	end

	.align 2
JohtoMart_Items::
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_ICE_HEAL
	.2byte ITEM_REVIVE
	.2byte ITEM_ESCAPE_ROPE
	.2byte ITEM_REPEL
	.2byte ITEM_SUPER_REPEL
	.2byte ITEM_NONE

EventScript_JohtoMomHeal::
	lock
	faceplayer
	msgbox JohtoMomHeal_Text_TakeAQuickRest
	closemessage
	call Common_EventScript_OutOfCenterPartyHeal
	msgbox JohtoMomHeal_Text_LookingGreat
	release
	end

JohtoMomHeal_Text_TakeAQuickRest:
	.string "You should take a quick rest.$"

JohtoMomHeal_Text_LookingGreat:
	.string "Looking great!\n"
	.string "Take care.$"
