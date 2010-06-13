//
//  CategoryTaskViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "CategoryTaskViewController.h"
#import "TaskDetailsController.h"
#import "String+Utils.h"
#import "Configuration.h"

#import "CDTask.h"
#import "CDTask+Addons.h"
#import "CDHierarchicalDomainObject+Addons.h"

#import "i18n.h"

@implementation CategoryTaskViewController

- initWithCategoryController:(CategoryViewController *)controller edit:(BOOL)edit category:(CDCategory *)theCategory
{
	if (self = [super initWithCategoryController:controller edit:edit])
	{
		category = [theCategory retain];
	}

	return self;
}

- (void)setCategory:(CDCategory *)theCategory
{
	// This is only used on the iPad

	[self.navigationController popToRootViewControllerAnimated:YES];

	[category release];
	category = [theCategory retain];

	if (category)
		self.navigationItem.title = category.name;
	else
		self.navigationItem.title = _("All");

	[self populate];

	// WTF? This doesn't work!
	[self.tableView reloadData];
}

- (void)dealloc
{
	[category release];
	[super dealloc];
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	if (category)
		self.navigationItem.title = category.name;
	else
		self.navigationItem.title = _("All");
}

- (void)viewWillAppear:(BOOL)animated
{
	[super viewWillAppear:animated];

	[self populate];
}

- (NSPredicate *)predicate
{
	if (category)
		return [NSPredicate predicateWithFormat:@"parent == NULL AND ANY categories IN %@", [category selfAndChildren]];
	else
		return [NSPredicate predicateWithFormat:@"parent == NULL"];
}

- (IBAction)onAddTask:(UIBarButtonItem *)button
{
	[super onAddTask:button];

	CDTask *task = (CDTask *)[NSEntityDescription insertNewObjectForEntityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()];
	task.creationDate = [NSDate date];
	task.file = [Configuration configuration].cdCurrentFile;
	task.name = @"";
	task.longDescription = @"";
	if (category)
		[task addCategoriesObject:category];
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
