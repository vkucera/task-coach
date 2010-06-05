//
//  BaseCategoryViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 02/08/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskCoachAppDelegate.h"
#import "BaseCategoryViewController.h"
#import "Database.h"
#import "Statement.h"
#import "BadgedCell.h"
#import "CellFactory.h"

#import "CDCategory.h"
#import "CDDomainObject+Addons.h"

static NSMutableArray *expandChildren(CDCategory *category, NSMutableDictionary *indentations, NSInteger indent)
{
	NSMutableArray *allChildren = [[[NSMutableArray alloc] init] autorelease];
	[allChildren addObject:category];
	[indentations setObject:[NSNumber numberWithInt:indent] forKey:[category objectID]];

	// XXXTODO: sort by name!

	for (CDCategory *child in [category children])
	{
		[allChildren addObjectsFromArray:expandChildren(child, indentations, indent + 1)];
	}

	return allChildren;
}

@implementation BaseCategoryViewController

#pragma mark View controller methods

- (void)viewDidLoad
{
	categories = [[NSMutableArray alloc] init];
	indentations = [[NSMutableDictionary alloc] init];
	
	[self loadCategories];
	
	[super viewDidLoad];
}

- (void)viewDidUnload
{
	[categories release];
	categories = nil;
	
	[indentations release];
	indentations = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)toInterfaceOrientation
{
	return YES;
}

#pragma mark Object lifetime

- (void)dealloc
{
	[self viewDidUnload];
	
	[super dealloc];
}

#pragma mark Domain methods

- (void)loadCategories
{
	[categories removeAllObjects];
	[indentations removeAllObjects];

	// We're assuming that there are not a bunch of categories, therefore we keep them in memory.
	// This is not the case with tasks.

	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDCategory" inManagedObjectContext:getManagedObjectContext()]];
	[request setPredicate:[NSPredicate predicateWithFormat:@"status != %d AND file == %@ AND parent == NULL", STATUS_DELETED,
						   [Database connection].cdCurrentFile]];
	NSSortDescriptor *sd = [[NSSortDescriptor alloc] initWithKey:@"name" ascending:YES];
	[request setSortDescriptors:[NSArray arrayWithObject:sd]];
	[sd release];
	
	NSError *error;
	NSArray *rootItems = [getManagedObjectContext() executeFetchRequest:request error:&error];
	[request release];

	if (!rootItems)
	{
		NSLog(@"Could not fetch categories: %@", [error localizedDescription]);
		return;
	}

	for (CDCategory *category in rootItems)
	{
		[categories addObjectsFromArray:expandChildren(category, indentations, 0)];
	}
}


- (void)fillCell:(BadgedCell *)cell forCategory:(CDCategory *)category
{
	[cell.badge clearAnnotations];
	cell.badge.text = nil;

	cell.textLabel.text = category.name;
	cell.textLabel.textColor = [UIColor blackColor];

	cell.indentationLevel = [[indentations objectForKey:[category objectID]] intValue];
	cell.accessoryType = UITableViewCellAccessoryNone;
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    return [categories count];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"BadgedCell";
	
    BadgedCell *cell = (BadgedCell *)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
	{
        cell = [[[CellFactory cellFactory] createBadgedCell] autorelease];
    }

	CDCategory *category = [categories objectAtIndex:indexPath.row];
	[self fillCell:cell forCategory:category];
	
    return cell;
}

@end

