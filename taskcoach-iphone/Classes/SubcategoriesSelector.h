//
//  SubcategoriesSelector.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/03/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

@class Category;

@interface SubcategoriesSelector : NSObject
{
	NSMutableArray *categoryIds;
}

- initWithCategory:(NSInteger)categoryId;

- (NSString *)clause;

@end
