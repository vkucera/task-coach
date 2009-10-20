//
//  BaseCategoryViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 02/08/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "BaseCategoryViewController.h"
#import "Category.h"
#import "Database.h"
#import "Statement.h"
#import "BadgedCell.h"
#import "CellFactory.h"

@implementation BaseCategoryViewController

- (void)addCategory:(NSDictionary *)dict
{
	Category *category = [[Category alloc] initWithId:[[dict objectForKey:@"id"] intValue] name:[dict objectForKey:@"name"]
											   status:[[dict objectForKey:@"status"] intValue] taskCoachId:[dict objectForKey:@"taskCoachId"]
											 parentId:[dict objectForKey:@"parentId"]];
	[categories addObject:category];
}

- (void)loadCategories
{
	[categories removeAllObjects];
	
	// We're assuming that there are not a bunch of categories, therefore we keep them in memory.
	// This is not the case with tasks.
	
	Statement *req = [[Database connection] statementWithSQL:@"SELECT * FROM Category WHERE status != ? ORDER BY name"];
	[req bindInteger:STATUS_DELETED atIndex:1];
	[req execWithTarget:self action:@selector(addCategory:)];
	
	NSMutableDictionary *dict = [[NSMutableDictionary alloc] initWithCapacity:8];
	NSMutableArray *rootItems = [[NSMutableArray alloc] initWithCapacity:8];
	
	for (Category *category in categories)
	{
		[dict setObject:category forKey:[NSNumber numberWithInt:category.objectId]];
		
		if (!category.parentId)
			[rootItems addObject:category];
	}
	
	for (Category *category in categories)
	{
		if (category.parentId)
		{
			Category *parent = [dict objectForKey:category.parentId];
			[parent addChild:category];
		}
	}
	
	[categories removeAllObjects];
	for (Category *category in rootItems)
	{
		[category finalizeChildren:categories];
	}
	
	[dict release];
	[rootItems release];
}


- (void)viewDidLoad
{
	categories = [[NSMutableArray alloc] init];
	[self loadCategories];
	
	[super viewDidLoad];
}

- (void)viewDidUnload
{
	[categories release];
	categories = nil;
}

- (void)dealloc
{
	[self viewDidUnload];
	
	[super dealloc];
}

- (void)fillCell:(BadgedCell *)cell forCategory:(Category *)category
{
	[cell.badge clearAnnotations];
	cell.badge.text = nil;

	cell.textLabel.text = category.name;
	cell.textLabel.textColor = [UIColor blackColor];

	cell.indentationLevel = category.level;
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

	Category *category = [categories objectAtIndex:indexPath.row];
	[self fillCell:cell forCategory:category];
	
    return cell;
}

@end

