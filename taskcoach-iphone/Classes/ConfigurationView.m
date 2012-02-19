//
//  ConfigurationView.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 23/10/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "ConfigurationView.h"
#import "Configuration.h"
#import "CellFactory.h"
#import "ButtonCell.h"
#import "ChoiceViewController.h"
#import "i18n.h"


@implementation ConfigurationView


#pragma mark -
#pragma mark View lifecycle

- init
{
	if ((self = [super initWithNibName:@"ConfigurationView" bundle:[NSBundle mainBundle]]))
	{
		// Nothing yet
	}
	
	return self;
}

- (void)setTarget:(id)theTarget action:(SEL)theAction
{
	target = theTarget;
	action = theAction;
}

- (void)viewDidLoad
{
    [super viewDidLoad];

	cells = [[NSMutableArray alloc] initWithCapacity:2];
	
	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
	{
		ButtonCell *btnCell = [[CellFactory cellFactory] createButtonCell];
		[btnCell.button setTitle:_("Done") forState:UIControlStateNormal];
		[btnCell setTarget:self action:@selector(onSave:)];
		[cells addObject:[NSArray arrayWithObject:btnCell]];
		firstSec = 1;
	}
	
	NSMutableArray *dpyCells = [[NSMutableArray alloc] initWithCapacity:4];

	SwitchCell *switchCell = [[CellFactory cellFactory] createSwitchCell];
	switchCell.label.text = _("Show completed");
	switchCell.switch_.on = [[Configuration configuration] showCompleted];
	[switchCell setDelegate:self];
	[dpyCells addObject:switchCell];
	
	switchCell = [[CellFactory cellFactory] createSwitchCell];
	switchCell.label.text = _("Show inactive");
	switchCell.switch_.on = [[Configuration configuration] showInactive];
	[switchCell setDelegate:self];
	[dpyCells addObject:switchCell];
	
	switchCell = [[CellFactory cellFactory] createSwitchCell];
	switchCell.label.text = _("Compact tasks");
	switchCell.switch_.on = [[Configuration configuration] compactTasks];
	[switchCell setDelegate:self];
	[dpyCells addObject:switchCell];

	UITableViewCell *cell = [[CellFactory cellFactory] createRegularCell];
	cell.textLabel.text = [NSString stringWithFormat:_("Position: %@"), ([Configuration configuration].iconPosition == ICONPOSITION_RIGHT) ? _("Right") : _("Left")];
	cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
	[dpyCells addObject:cell];
	
	cell = [[CellFactory cellFactory] createRegularCell];
	cell.textLabel.text = [NSString stringWithFormat:_("Display: %@"), ([Configuration configuration].dpyStyle == DPY_TREE) ? _("Tree") : _("List")];
	cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
	[dpyCells addObject:cell];
	
	switchCell = [[CellFactory cellFactory] createSwitchCell];
	switchCell.label.text = _("Show composite");
	switchCell.switch_.on = [Configuration configuration].showComposite;
	[switchCell setDelegate:self];
	[dpyCells addObject:switchCell];
	
	[cells addObject:dpyCells];
	[dpyCells release];
	
	dpyCells = [[NSMutableArray alloc] initWithCapacity:2];

	switchCell = [[CellFactory cellFactory] createSwitchCell];
	switchCell.label.text = _("Confirm complete");
	switchCell.switch_.on = [[Configuration configuration] confirmComplete];
	[switchCell setDelegate:self];
	[dpyCells addObject:switchCell];

	RecurrencePeriodCell *dueCell = [[CellFactory cellFactory] createRecurrencePeriodCell];
	[dueCell setDelegate:self];
	dueCell.textField.text = [NSString stringWithFormat:@"%d", [Configuration configuration].soonDays];
	dueCell.label.text = _("Due soon # of days");
	[dpyCells addObject:dueCell];
	[dueCell release];

	[cells addObject:dpyCells];
	[dpyCells release];
}

- (void)viewDidUnload
{
	[cells release];
	cells = nil;
}


- (void)dealloc
{
	[self viewDidUnload];

    [super dealloc];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
	return YES;
}


#pragma mark -
#pragma mark Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
	return [cells count];
}


- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	if ((section == firstSec) && ([Configuration configuration].dpyStyle == DPY_TREE))
		return [[cells objectAtIndex:section] count] - 1;
	return [[cells objectAtIndex:section] count];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
	return [[cells objectAtIndex:indexPath.section] objectAtIndex:indexPath.row];
}

#pragma mark -
#pragma mark Table view delegate

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	[self.tableView deselectRowAtIndexPath:indexPath animated:YES];

	if (indexPath.section == firstSec)
	{
		UIViewController *ctrl = nil;

		switch (indexPath.row)
		{
			case 3:
				ctrl = [[ChoiceViewController alloc] initWithChoices:[NSArray arrayWithObjects:_("Right"), _("Left"), nil] current:[Configuration configuration].iconPosition target:self action:@selector(onSetIconDirection:)];
				break;
			case 4:
				ctrl = [[ChoiceViewController alloc] initWithChoices:[NSArray arrayWithObjects:_("Tree"), _("List"), nil] current:[Configuration configuration].dpyStyle target:self action:@selector(onSetDisplayStyle:)];
				break;
			default:
				break;
		}

		if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
		{
			ctrl.modalPresentationStyle = UIModalPresentationFormSheet;
		}

		[self presentModalViewController:ctrl animated:YES];
		[ctrl release];
	}
}

#pragma mark -
#pragma mark Actions and callbacks

- (void)onSave:(ButtonCell *)cell
{
	[[Configuration configuration] save];

	if (target)
	{
		[target performSelector:action];
	}

	[self dismissModalViewControllerAnimated:YES];
}

- (void)onSwitchValueChanged:(SwitchCell *)cell
{
	if (cell == [[cells objectAtIndex:firstSec] objectAtIndex:0])
	{
		[[Configuration configuration] setShowCompleted:cell.switch_.on];
	}
	else if (cell == [[cells objectAtIndex:firstSec] objectAtIndex:1])
	{
		[[Configuration configuration] setShowInactive:cell.switch_.on];
	}
	else if (cell == [[cells objectAtIndex:firstSec] objectAtIndex:2])
	{
		[[Configuration configuration] setCompactTasks:cell.switch_.on];
	}
	else if (cell == [[cells objectAtIndex:firstSec] objectAtIndex:5])
	{
		[[Configuration configuration] setShowComposite:cell.switch_.on];
	}

	if (cell == [[cells objectAtIndex:firstSec + 1] objectAtIndex:0])
	{
		[[Configuration configuration] setConfirmComplete:cell.switch_.on];
	}

	if ((UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad) && target)
	{
		[target performSelector:action];
	}
}

- (void)onSetIconDirection:(NSNumber *)position
{
	[Configuration configuration].iconPosition = [position intValue];

	UITableViewCell *cell = [[cells objectAtIndex:firstSec] objectAtIndex:3];
	cell.textLabel.text = [NSString stringWithFormat:_("Position: %@"), ([Configuration configuration].iconPosition == ICONPOSITION_RIGHT) ? _("Right") : _("Left")];

	[self dismissModalViewControllerAnimated:YES];
}

- (void)onSetDisplayStyle:(NSNumber *)style
{
	if ([style intValue] != [Configuration configuration].dpyStyle)
	{
		[Configuration configuration].dpyStyle = [style intValue];

		switch ([style intValue])
		{
			case DPY_TREE:
				[self.tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:5 inSection:firstSec]] withRowAnimation:UITableViewRowAnimationRight];
				break;
			case DPY_LIST:
				[self.tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:5 inSection:firstSec]] withRowAnimation:UITableViewRowAnimationRight];
				break;
		}
	}

	UITableViewCell *cell = [[cells objectAtIndex:firstSec] objectAtIndex:4];
	cell.textLabel.text = [NSString stringWithFormat:_("Display: %@"), ([Configuration configuration].dpyStyle == DPY_TREE) ? _("Tree") : _("List")];
	
	[self dismissModalViewControllerAnimated:YES];
}

- (void)recurrencePeriodCell:(RecurrencePeriodCell *)cell valueDidChange:(NSInteger)newValue
{
	[Configuration configuration].soonDays = newValue;
}

@end

