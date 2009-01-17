//
//  CategoryViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "CategoryViewController.h"
#import "StringChoiceController.h"
#import "TaskViewController.h"

#import "Database/Database.h"
#import "Database/Statement.h"

#import "Domain/Category.h"

@implementation CategoryViewController

- (void)addCategory:(NSDictionary *)dict
{
	Category *category = [[Category alloc] initWithId:[[dict objectForKey:@"id"] intValue] name:[dict objectForKey:@"name"] status:[[dict objectForKey:@"status"] intValue]];
	[categories addObject:category];
}

- (void)loadCategories
{
	[categories release];

	// We're assuming that there are not a bunch of categories, therefore we keep them in memory.
	// This is not the case with tasks.
	
	categories = [[NSMutableArray alloc] initWithCapacity:8];
	Statement *req = [[Database connection] statementWithSQL:@"SELECT * FROM Category WHERE status != 3 ORDER BY name"];
	[req execWithTarget:self action:@selector(addCategory:)];
}

- (void)viewDidLoad
{
	[self loadCategories];

	[super viewDidLoad];
}

- (void)childWasPopped
{
	NSIndexPath *indexPath = [self.tableView indexPathForSelectedRow];
	
	if (indexPath)
	{
		[self.tableView deselectRowAtIndexPath:indexPath animated:YES];
	}
}

- (void)dealloc
{
	[categories release];

    [super dealloc];
}

- (IBAction)onAddCategory:(UIBarButtonItem *)button
{
	StringChoiceController *ctrl = [[StringChoiceController alloc] initWithPlaceholder:NSLocalizedString(@"Enter category name", @"New category placeholder") target:self action:@selector(onCategoryAdded:)];
	[self presentModalViewController:ctrl animated:YES];
	[ctrl release];
}

- (void)onCategoryAdded:(NSString *)name
{
	if (name != nil)
	{
		Statement *req = [[Database connection] statementWithSQL:@"INSERT INTO Category (name) VALUES (?)"];
		[req bindString:name atIndex:1];
		[req exec];
		[self loadCategories];
		[self.tableView reloadData];
	}

	[self dismissModalViewControllerAnimated:YES];
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    return [categories count] + 1;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";

    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
	{
        cell = [[[UITableViewCell alloc] initWithFrame:CGRectZero reuseIdentifier:CellIdentifier] autorelease];
		cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
    }
    
	if (indexPath.row)
	{
		cell.text = [[categories objectAtIndex:indexPath.row - 1] name];
	}
	else
	{
		cell.text = NSLocalizedString(@"All", @"All categories name");
	}

    return cell;
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	TaskViewController *ctrl;
	
	if (indexPath.row)
	{
		ctrl = [[TaskViewController alloc] initWithTitle:[[categories objectAtIndex:indexPath.row - 1] name] category:[[categories objectAtIndex:indexPath.row - 1] objectId]];
	}
	else
	{
		ctrl = [[TaskViewController alloc] initWithTitle:NSLocalizedString(@"All", @"All categories view title") category:-1];
	}

	[self.navigationController pushViewController:ctrl animated:YES];
	[ctrl release];
}

@end

