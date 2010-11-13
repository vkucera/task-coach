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
	cell.accessoryType = UITableViewCellAccessoryNone;
	[dpyCells addObject:cell];

	[cells addObject:dpyCells];
	[dpyCells release];
	
	dpyCells = [[NSMutableArray alloc] initWithCapacity:2];

	switchCell = [[CellFactory cellFactory] createSwitchCell];
	switchCell.label.text = _("Confirm complete");
	switchCell.switch_.on = [[Configuration configuration] confirmComplete];
	[switchCell setDelegate:self];
	[dpyCells addObject:switchCell];

	[cells addObject:dpyCells];
	[dpyCells release];

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
	{
		ButtonCell *btnCell = [[CellFactory cellFactory] createButtonCell];
		[btnCell.button setTitle:_("Done") forState:UIControlStateNormal];
		[btnCell setTarget:self action:@selector(onSave:)];
		[cells addObject:[NSArray arrayWithObject:btnCell]];
	}
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
	if ((indexPath.section == 0) && (indexPath.row == 3))
	{
		[self.tableView deselectRowAtIndexPath:indexPath animated:YES];
		ChoiceViewController *ctrl = [[ChoiceViewController alloc] initWithChoices:[NSArray arrayWithObjects:_("Right"), _("Left"), nil] current:[Configuration configuration].iconPosition target:self action:@selector(onSetIconDirection:)];
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
	if (cell == [[cells objectAtIndex:0] objectAtIndex:0])
	{
		[[Configuration configuration] setShowCompleted:cell.switch_.on];
	}
	else if (cell == [[cells objectAtIndex:0] objectAtIndex:1])
	{
		[[Configuration configuration] setShowInactive:cell.switch_.on];
	}
	else if (cell == [[cells objectAtIndex:0] objectAtIndex:2])
	{
		[[Configuration configuration] setCompactTasks:cell.switch_.on];
	}

	if (cell == [[cells objectAtIndex:1] objectAtIndex:0])
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
	[[Configuration configuration] save];

	UITableViewCell *cell = [[cells objectAtIndex:0] objectAtIndex:3];
	cell.textLabel.text = [NSString stringWithFormat:_("Position: %@"), ([Configuration configuration].iconPosition == ICONPOSITION_RIGHT) ? _("Right") : _("Left")];

	[self dismissModalViewControllerAnimated:YES];
}

@end

