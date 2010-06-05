//
//  ParentTaskViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 05/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "ParentTaskViewController.h"
#import "TaskDetailsController.h"
#import "TaskCoachAppDelegate.h"
#import "i18n.h"
#import "CDTask+Addons.h"

@implementation ParentTaskViewController

- initWithCategoryController:(CategoryViewController *)controller edit:(BOOL)edit parent:(CDTask *)theParent
{
	if (self = [super initWithCategoryController:controller edit:edit])
	{
		parent = [theParent retain];

		[self populate];
	}

	return self;
}

- (void)dealloc
{
	[parent release];
	[super dealloc];
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	self.navigationItem.title = parent.name;
}

- (NSPredicate *)predicate
{
	return [NSPredicate predicateWithFormat:@"parent == %@", parent];
}

- (IBAction)onAddTask:(UIBarButtonItem *)button
{
	[super onAddTask:button];
	
	CDTask *task = (CDTask *)[NSEntityDescription insertNewObjectForEntityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()];
	task.name = @"";
	task.longDescription = @"";
	task.parent = parent;
	[task computeDateStatus];

	NSError *error;
	if ([getManagedObjectContext() save:&error])
	{
		TaskDetailsController *ctrl = [[TaskDetailsController alloc] initWithTask:task];
		[self.navigationController pushViewController:ctrl animated:YES];
		[ctrl release];
	}
	else
	{
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
		[alert show];
		[alert release];
		NSLog(@"Error: %@", [error localizedDescription]);
	}
}

@end
