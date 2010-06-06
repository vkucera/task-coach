//
//  TaskCategoryPickerController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 02/08/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskCoachAppDelegate.h"

#import "TaskCategoryPickerController.h"
#import "BadgedCell.h"

#import "CDDomainObject+Addons.h"
#import "CDTask.h"

#import "i18n.h"

@implementation TaskCategoryPickerController

#pragma mark Object lifetime

- initWithTask:(CDTask *)task
{
	if (self = [super initWithNibName:@"TaskCategoryPicker" bundle:[NSBundle mainBundle]])
	{
		myTask = [task retain];
	}
	
	return self;
}

- (void)dealloc
{
	[myTask release];
	
	[super dealloc];
}

#pragma mark Domain methods

- (void)fillCell:(BadgedCell *)cell forCategory:(CDCategory *)category
{
	[super fillCell:cell forCategory:category];

	if ([[myTask categories] containsObject:category])
	{
		cell.accessoryType = UITableViewCellAccessoryCheckmark;
	}
}

#pragma mark Table view methods

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	CDCategory *category = [categories objectAtIndex:indexPath.row];
	BadgedCell *cell = (BadgedCell *)[self.tableView cellForRowAtIndexPath:indexPath];

	if ([[myTask categories] containsObject:category])
	{
		[myTask removeCategoriesObject:category];
		cell.accessoryType = UITableViewCellAccessoryNone;
	}
	else
	{
		[myTask addCategoriesObject:category];
		cell.accessoryType = UITableViewCellAccessoryCheckmark;
	}

	[myTask markDirty];
	NSError *error;
	if (![getManagedObjectContext() save:&error])
	{
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
		[alert show];
		[alert release];
	}

	[self.tableView deselectRowAtIndexPath:indexPath animated:YES];
}

@end
